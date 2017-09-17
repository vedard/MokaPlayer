import pathlib
from gi.repository import GdkPixbuf

def load(filename, width, height):
    if not filename or not pathlib.Path(filename).is_file():
        filename = 'musicplayer/resources/placeholder.png'

    pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
    pixbuf = pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
    return pixbuf
