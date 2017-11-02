from gi.repository import Gtk
from mokaplayer.core.helpers import time_helper


class AdapterSongFromAlbum:
    @staticmethod
    def create_row(song):
        return [
            song.Path,
            str(song.Tracknumber) + ".",
            song.Title or 'Unknown',
            time_helper.seconds_to_string(song.Length)
        ]

    @staticmethod
    def create_store():
        model = Gtk.ListStore(str, str, str, str)
        model.set_default_sort_func(lambda *unused: 0)
        model.set_sort_column_id(
            Gtk.TREE_SORTABLE_UNSORTED_SORT_COLUMN_ID, Gtk.SortType.ASCENDING)
        return model

    @staticmethod
    def create_col_number():
        return [0, 1, 2, 3]
