# -*- coding: utf-8 -*-
import click
from tatortot import viewer

@click.command()
@click.argument('src', type=click.Path(exists=True))
@click.argument('dest', type=click.Path(exists=True))
def main(src, dest):
    # note: blitting is needed, but on mac monitor it does wonkiness unless the canvas size perfect
    # matches the image size. so keep width at 325 to avoid this.
    tator_viewer = viewer.DirectoryViewer(src_dir=src, dest_dir=dest, useblit=True, size=(325, 800))


    super_pixels = viewer.SuperPixelPlugin()
    tator_viewer += super_pixels
    brush_tool = viewer.RegionBrush(tator_viewer, (256, 256), 2, 0.2)

    tator_viewer.show()

if __name__ == '__main__':
    main()
