import pathlib
import pkg_resources

from multiprocessing.pool import ThreadPool

from gi.repository import GdkPixbuf
from gi.repository import GObject
from gi.repository import Gdk


def load(filename, width, height, screen_scale_factor):
    if not filename or not pathlib.Path(filename).is_file():
        filename = pkg_resources.resource_filename('mokaplayer', 'data/placeholder.png')

    pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
    pixbuf = pixbuf.scale_simple(width * screen_scale_factor, height * screen_scale_factor, GdkPixbuf.InterpType.BILINEAR)
    return pixbuf


def set_image(gtkimage, filename, width, height):
    screen_scale_factor = gtkimage.get_scale_factor()
    pixbuf = load(filename, width, height, screen_scale_factor)
    GObject.idle_add(lambda: gtkimage.set_from_surface(Gdk.cairo_surface_create_from_pixbuf(pixbuf, screen_scale_factor)))


def set_multiple_image(list_tuples):
    pool = ThreadPool(4)
    for x in list_tuples:
        pool.apply_async(set_image, x)
