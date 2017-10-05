from gi.repository import Gtk
import arrow
import re

from musicplayer.core.helpers import time_helper


class AdapterSong:
    @staticmethod
    def create_row(song):
        return [
            song.Path,
            song.Title or 'Unkown',
            song.AlbumArtist or 'Unkown',
            song.Album or 'Unkown',
            time_helper.seconds_to_string(song.Length),
            song.Year or '0000',
            arrow.Arrow(song.Added.year, song.Added.month, song.Added.day).humanize(),
            song.Played,
            song.Genre
        ]

    @staticmethod
    def create_store():
        return Gtk.ListStore(str, str, str, str, str, str, str, str, str)

    @staticmethod
    def create_col_number():
        return [0, 1, 2, 3, 4, 5, 6, 7, 8]

    @staticmethod
    def search(text, row):
        if not text:
            return True
        else:
            try:
                return any(re.search(text, col, re.RegexFlag.IGNORECASE) for col in row)
            except re.error:
                return False  # regex syntax error
