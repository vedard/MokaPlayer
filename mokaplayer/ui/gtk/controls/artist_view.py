from gi.repository import Gtk
from . import AlbumView


class ArtistView:
    def __init__(self, artist_playlist, row_activated, button_press_event):
        self.artist_playlist = artist_playlist
        self.view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.view.pack_start(Gtk.Separator(margin_bottom=5, margin_left=10, margin_right=10, margin_top=0), False, True, 0)

        for album_playlist in artist_playlist.collections_album():
            self.view.pack_start(AlbumView(album_playlist,
                                           row_activated,
                                           button_press_event).get_view(), False, False, 0)
        self.view.show_all()

    def get_view(self):
        return self.view
