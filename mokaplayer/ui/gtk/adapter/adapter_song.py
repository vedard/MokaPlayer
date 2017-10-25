import re

import arrow
from gi.repository import Gtk
from mokaplayer.core.helpers import time_helper


class AdapterSong:
    @staticmethod
    def create_row(song):
        return [
            song.Path,
            song.Title or 'Unknown',
            song.AlbumArtist or 'Unknown',
            song.Album or 'Unknown',
            time_helper.seconds_to_string(song.Length),
            song.Year or '0000',
            arrow.Arrow(song.Added.year, song.Added.month, song.Added.day).humanize(),
            song.Played,
            song.Genre,
            str(song.Tracknumber)
        ]

    @staticmethod
    def create_store():
        model = Gtk.ListStore(str, str, str, str, str, str, str, str, str, str)
        model.set_default_sort_func(lambda *unused: 0)
        model.set_sort_column_id(Gtk.TREE_SORTABLE_UNSORTED_SORT_COLUMN_ID, Gtk.SortType.ASCENDING)
        return model

    @staticmethod
    def create_col_number():
        return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    @staticmethod
    def search(text, row):
        if not text:
            return True
        else:
            try:
                return any(re.search(text, col, re.RegexFlag.IGNORECASE) for col in row)
            except re.error:
                return False  # regex syntax error
