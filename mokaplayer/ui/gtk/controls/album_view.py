import pkg_resources

from gi.repository import Gtk

from mokaplayer.ui.gtk.helper import image_helper
from mokaplayer.ui.gtk.adapter.adapter_song_from_album import AdapterSongFromAlbum


class AlbumView:
    GLADE_FILE = pkg_resources.resource_filename('mokaplayer', 'data/ui/album_view.ui')

    def __init__(self, album_playlist, row_activated, button_press_event, hide_header=False):
        self.album_playlist = album_playlist
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.GLADE_FILE)

        self.view = self.builder.get_object("view")
        self.grid_songs = self.builder.get_object("grid_songs")
        self.img_cover = self.builder.get_object("img_cover")
        self.lbl_album_name = self.builder.get_object("lbl_album_name")
        self.lbl_year = self.builder.get_object("lbl_year")
        self.header = self.builder.get_object("header")

        self.grid_songs.connect('row-activated', row_activated)
        self.grid_songs.connect('button-press-event', button_press_event)
        self.grid_songs.connect('focus-in-event', self.on_grid_songs_focus_in_event)

        if hide_header:
            self.view.remove(self.header)
        else:
            self.lbl_album_name.set_text(self.album_playlist.album.Name)
            self.lbl_year.set_text(self.album_playlist.album.Year)

        image_helper.set_image(self.img_cover, album_playlist.album.Cover, 220, 220)

        self._build_grid_songs()

    def get_view(self):
        return self.view

    def on_grid_songs_focus_in_event(self, widget, event):
        """ We don't want 2 treeview with a selection,
            so we walk trougth the siblings and their children
            then call unselect_all() if it's a treeview
        """
        stack = [self.get_view().get_parent()]
        while any(stack):
            element = stack.pop()
            if isinstance(element, Gtk.TreeView) and element is not widget:
                element.get_selection().unselect_all()
            elif isinstance(element, Gtk.Container):
                stack.extend(element.get_children())

    def _build_grid_songs(self):
        model = AdapterSongFromAlbum.create_store()

        for song in self.album_playlist.collections():
            model.insert_with_valuesv(-1,
                                      AdapterSongFromAlbum.create_col_number(),
                                      AdapterSongFromAlbum.create_row(song))
        self.grid_songs.set_model(model)
