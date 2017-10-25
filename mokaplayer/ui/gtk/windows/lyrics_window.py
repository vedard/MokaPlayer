from threading import Thread

import pkg_resources
from gi.repository import GObject, Gtk
from mokaplayer.core.database import Song
from mokaplayer.core.fetchers import lyrics


class LyricsWindow():
    GLADE_FILE = pkg_resources.resource_filename('mokaplayer',
                                                 'data/ui/lyrics_window.ui')

    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.GLADE_FILE)
        self.builder.connect_signals(self)
        self.window = self.builder.get_object('lyrics_window')
        self.lbl_title = self.builder.get_object('lbl_title')
        self.txt_lyrics = self.builder.get_object('txt_lyrics')

    def start_fetch(self, song):
        self.song = song
        self.txt_lyrics.get_buffer().set_text('')

        if self.song is not None:
            self.lbl_title.set_text(f'{self.song.Title} - {self.song.Artist}')
            Thread(target=self.fetch).start()
        else:
            self.lbl_title.set_text('')

    def fetch(self):
        ly = self.song.Lyrics

        if not ly:
            success, ly = lyrics.get(self.song.Title, self.song.Artist, self.song.Album)
            if success:
                self.song.Lyrics = ly
                self.song.save()
        else:
            ly = ly + ' (cached)'

        GObject.idle_add(lambda: self.on_fetch_finished(ly))

    def on_fetch_finished(self, ly):
        self.txt_lyrics.get_buffer().set_text(ly)

    def get_window(self):
        return self.window

    def on_btn_refresh_clicked(self, widget):
        if self.song is not None:
            self.song.Lyrics = None
            self.start_fetch(self.song)
