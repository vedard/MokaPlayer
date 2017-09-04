from gi.repository import Gtk
import arrow
import re

class AdapterSong:
    @staticmethod
    def create_row(song):
        return [
            song.Path,
            song.Title or 'Unknown',
            song.AlbumArtist or 'Unknown',
            song.Album or 'Unknown',
            arrow.get(0).shift(seconds=song.Length).format('mm:ss'),
            song.Year,
            arrow.get(song.Added).humanize()
        ]
    
    @staticmethod
    def create_store():
        return Gtk.ListStore(str,str,str,str,str,str,str)
    
    @staticmethod
    def search(text, row):
        if not text:
            return True
        else:
            return any(re.search(text, col, re.RegexFlag.IGNORECASE) for col in row)
