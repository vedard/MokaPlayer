import pathlib
import pkg_resources

from multiprocessing.pool import ThreadPool

from gi.repository import GdkPixbuf
from gi.repository import GObject


def load(filename, width, height):
    if not filename or not pathlib.Path(filename).is_file():
        filename = pkg_resources.resource_filename('mokaplayer', 'data/placeholder.png')

    pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
    pixbuf = pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
    return pixbuf


def set_image(gtkimage, filename, width, height):
    pixbuf = load(filename, width, height)
    GObject.idle_add(lambda: gtkimage.set_from_pixbuf(pixbuf))


def set_multiple_image(list_tuples):
    pool = ThreadPool(4)
    for x in list_tuples:
        pool.apply_async(set_image, x)
