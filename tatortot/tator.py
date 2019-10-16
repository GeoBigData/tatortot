# -*- coding: utf-8 -*-
import click
from tatortot import viewer

@click.command()
@click.argument('src', type=click.Path(exists=True))
@click.argument('dest', type=click.Path(exists=True))
@click.option('--img_width', '-w', type=int, default=256,
              help="Width of src images in pixels. Default is 256")
@click.option('--img_height', '-h', type=int, default=256,
              help="Height of src images in pixels. Default is 256")
@click.option('--viewer_width', '-W', type=int, default=325,
              help="Width of viewer in pixels. Default is 325")
@click.option('--viewer_height', '-H', type=int, default=800,
              help="Height of viewer in pixels. Default is 800")
@click.option('--filetype', '-f', type=str, default='.jpeg',
              help="File format for src images (as file extension). Default is '.jpeg'")
def main(src, dest, img_width=256, img_height=256, viewer_width=326, viewer_height=300, filetype='.jpeg'):
    # note: blitting is needed, but on mac monitor it does wonkiness unless the canvas size perfect
    # matches the image size. so keep width at 325 to avoid this.
    tator_viewer = viewer.DirectoryViewer(src_dir=src, dest_dir=dest, useblit=True,
                                          size=(viewer_width, viewer_height), type=filetype)


    super_pixels = viewer.SuperPixelPlugin()
    tator_viewer += super_pixels
    brush_tool = viewer.RegionBrush(tator_viewer, (img_height, img_width), 2, 0.2)

    tator_viewer.show()

if __name__ == '__main__':
    main()
