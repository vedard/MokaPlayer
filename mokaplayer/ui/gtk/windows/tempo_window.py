import pkg_resources
from mokaplayer.core.streamer import Streamer
from gi.repository import Gtk


class TempoWindow():
    GLADE_FILE = pkg_resources.resource_filename('mokaplayer',
                                                 'data/ui/playback_window.ui')

    def __init__(self, streamer: Streamer):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.GLADE_FILE)
        self.builder.connect_signals(self)
        self.window = self.builder.get_object('playback_window')
        self.spin_speed = self.builder.get_object('spin_speed')
        self.streamer = streamer

    def on_btn_clicked(self, widget):
        self.streamer.set_playback_speed(self.spin_speed.get_value() / 100)

    def on_normal_clicked(self, widget):
        self.streamer.set_playback_speed(1.0)

    def get_window(self):
        return self.window
