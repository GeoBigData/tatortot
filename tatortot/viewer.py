import numpy as np
from skimage import io
from skimage.viewer.canvastools import PaintTool
from skimage.viewer import ImageViewer, CollectionViewer
from skimage.viewer.plugins.base import Plugin
from skimage import segmentation
from skimage.viewer import widgets
from functools import partial
import glob
from skimage.viewer.qt import QtWidgets, QtCore, QtGui
from skimage.viewer.utils import dialogs
from skimage.util import img_as_ubyte
import os
from matplotlib import colors

class SuperPixelPlugin(Plugin):
    """Canny filter plugin to show edges of an image."""

    name = 'SuperPixelPlugin'

    def __init__(self, *args, **kwargs):
        super(SuperPixelPlugin, self).__init__(**kwargs)

    def clear_overlays(self):

        viewer_tools = self.image_viewer._tools
        for tool in viewer_tools:
            if isinstance(tool, RegionBrush):
                tool.reset_overlay()

    def toggle_boundaries(self, name, value):

        image = self.arguments[0]
        if self.show_boundaries.val is True:
            filtered = segmentation.mark_boundaries(image, self.segments, mode='inner')
        else:
            filtered = image
        self.display_filtered_image(filtered)
        self.image_changed.emit(filtered)

    def _image_filter(self, *arguments, **kwargs):

        image = arguments[0]
        self.segments = self.seg_func(image, **kwargs)
        # self.clear_overlays()
        if self.show_boundaries.val is True:
            return segmentation.mark_boundaries(image, self.segments, mode='inner')
        else:
            return image

    def remove_widget(self, widget):

        # remove from arguments or kw arguments
        self.keyword_arguments = {k: v for k, v in self.keyword_arguments.items() if k != widget.name}
        new_arguments = [v for v in self.arguments[1:] if v.name != widget.name]
        self.arguments = self.arguments[0:1] + new_arguments
        # remove from layout
        widget.setParent(None)

    def add_sliders(self, name, value):

        layout_widgets = [self.layout.itemAt(i).widget() for i in range(1, self.layout.count())]
        for w in layout_widgets:
            self.remove_widget(w)

        if self.methods[value] == 'SLIC':
            self.add_widget(widgets.Slider('n_segments', 2, 500, value=150, update_on='release', value_type='int'))
            self.add_widget(widgets.Slider('compactness', 0, 10, value=8.75, update_on='release', value_type='float'))
            self.add_widget(widgets.Slider('max_iter', 0, 10, value=10, update_on='release', value_type='int'))
            self.add_widget(widgets.Slider('sigma', 0, 10, value=1, update_on='release', value_type='int'))
            self.seg_func = segmentation.slic

        elif self.methods[value] == 'Quickshift':
            self.add_widget(widgets.Slider('ratio', 0, 1, update_on='release', value_type='float'))
            self.add_widget(widgets.Slider('kernel_size', 1, 10, update_on='release', value_type='float'))
            self.add_widget(widgets.Slider('max_dist', 1, 10, update_on='release', value_type='float'))
            self.add_widget(widgets.Slider('sigma', 0, 10, update_on='release', value_type='int'))
            self.seg_func = segmentation.quickshift

        self.filter_image()
        # self.show()

    def add_nonimage_widget(self, widget, callback):
        """Add widget to plugin.
        Alternatively, Plugin's `__add__` method is overloaded to add widgets::
            plugin += Widget(...)
        Widgets can adjust required or optional arguments of filter function or
        parameters for the plugin. This is specified by the Widget's `ptype`.
        """

        widget.callback = callback
        widget.plugin = self
        self.layout.addWidget(widget, self.row, 0)
        self.row += 1

    def attach(self, image_viewer):

        self.show_boundaries = widgets.CheckBox(name='Show Boundaries', value=True)
        self.add_nonimage_widget(self.show_boundaries, callback=partial(self.toggle_boundaries))

        self.methods = ['SLIC', 'Quickshift']
        self.add_nonimage_widget(widgets.ComboBox(name='method', items=self.methods, ptype='kwarg'),
                                 callback=partial(self.add_sliders))
        self.add_sliders('method', 0)

        self.image_filter = partial(self._image_filter)
        # Call parent method at end b/c it calls `filter_image`, which needs
        # the values specified by the widgets. Alternatively, move call to
        # parent method to beginning and add a call to `self.filter_image()`
        super(SuperPixelPlugin, self).attach(image_viewer)


class RegionBrush(PaintTool):

    name = 'RegionBrush'

    def __init__(self, manager, overlay_shape, radius=2, alpha=0.2,
                 tableau_color='pink',
                 on_move=None, on_release=None, on_enter=None,
                 rect_props=None):

        self.tableau_color = tableau_color
        self.hex_color = colors.TABLEAU_COLORS['tab:{}'.format(tableau_color)]
        self.rgba_color = list(colors.to_rgba(self.hex_color))
        self.rgba_color[3] = alpha
        self.colors = np.zeros((overlay_shape[0], overlay_shape[1], 4))
        for i in range(0,4):
            self.colors[:, :, i] = self.rgba_color[i]
        super(RegionBrush, self).__init__(manager, overlay_shape, radius=radius, alpha=alpha,
                                          on_move=on_move, on_release=on_release, on_enter=on_enter,
                                          rect_props=rect_props)
        self.manager.reload_mask()

    def update_overlay(self, x, y, button):

        segments = self.manager.plugins[0].segments
        segment_i = np.bincount(segments[self.window.at(y, x)].ravel()).argmax()

        overlay = self.overlay

        if button == 1:
            new_value = self.label
        elif button == 3:
            new_value = 0

        overlay[segments == segment_i] = new_value
        # Note that overlay calls `redraw`
        self.overlay = overlay

    def on_mouse_press(self, event):
        self.update_cursor(event.xdata, event.ydata)
        if not self.ax.in_axes(event):
            return
        self.update_overlay(event.xdata, event.ydata, event.button)

    def reset_overlay(self):

        self.overlay = np.zeros(self.shape)

    def load_overlay(self, o):

        overlay = self.overlay
        overlay[o] = self.label
        if self._overlay_plot in self.ax.images:
            self.ax.images.remove(self._overlay_plot)
        self.overlay = overlay

    @property
    def overlay(self):
        return self._overlay

    @overlay.setter
    def overlay(self, image):
        self._overlay = image
        if image is None:
            self.ax.images.remove(self._overlay_plot)
            self._overlay_plot = None
        elif self._overlay_plot is None:
            overlay_image = self.colors * image[:, :, np.newaxis]
            self._overlay_plot = self.ax.imshow(overlay_image, animated=True)
        else:
            overlay_image = self.colors * image[:, :, np.newaxis]
            self._overlay_plot.set_data(overlay_image)
        self.redraw()


class DirectoryViewer(CollectionViewer):
    """Viewer for displaying image collections.
    Select the displayed frame of the image collection using the slider or
    with the following keyboard shortcuts:
        left/right arrows
            Previous/next image in collection.
        number keys, 0--9
            0% to 90% of collection. For example, "5" goes to the image in the
            middle (i.e. 50%) of the collection.
        home/end keys
            First/last image in collection.
    Parameters
    ----------
    image_collection : list of images
        List of images to be displayed.
    update_on : {'move' | 'release'}
        Control whether image is updated on slide or release of the image
        slider. Using 'on_release' will give smoother behavior when displaying
        large images or when writing a plugin/subclass that requires heavy
        computation.
    """

    def __init__(self, src_dir, dest_dir, size=(800,800), type='.jpeg', update_on='move', useblit=False, **kwargs):
        self.src_dir = src_dir
        self.dest_dir = dest_dir
        self.images = [os.path.join(self.src_dir, f) for f in glob.glob1(src_dir, '*{}'.format(type))]
        self.type = type
        self.ix = 0
        first_image = io.imread(self.images[self.ix])
        super(DirectoryViewer, self).__init__(first_image)
        # TODO: useblit must be False for my mac but not my big monitors...wtf is blit?
        self.useblit = useblit
        self.update_image(first_image)

        self.previous = widgets.Button('Previous Image', callback=self.rewind)
        self.next = widgets.Button('Next Image', self.advance)
        self.layout.addWidget(self.previous)
        self.layout.addWidget(self.next)

        self.slider.setParent(None)

        self.resize(*size)

    def reload_mask(self):

        # reload saved mask (if exists)
        mask_path = os.path.join(self.dest_dir, os.path.basename(self.images[self.ix]).replace(self.type, '.png'))
        self._tools[0].reset_overlay()
        if os.path.exists(mask_path):
            self._tools[0].reset_overlay()
            mask = io.imread(mask_path) == 255
            self._tools[0].load_overlay(mask)

    def rewind(self):

        self.ix = np.maximum(0, self.ix-1)
        image = io.imread(self.images[self.ix])
        self.update_image(image)
        self.reload_mask()

    def advance(self):

        self.save_mask()
        self.ix = np.minimum(len(self.images), self.ix + 1)
        image = io.imread(self.images[self.ix])
        self.update_image(image)
        self.reload_mask()

    def save_mask(self):

        mask = self._tools[0].overlay.astype(bool)
        mask = img_as_ubyte(mask)
        out_name = os.path.join(self.dest_dir, os.path.basename(self.images[self.ix]).replace(self.type, '.png'))
        io.imsave(out_name, mask)

    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent:
            key = event.key()
            if key == 49:
                self.rewind()
            elif key == 50:
                self.advance()
            else:
                event.ignore()
        else:
            event.ignore()

