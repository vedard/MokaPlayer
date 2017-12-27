import pkg_resources
from mokaplayer.core.streamer import Streamer
from gi.repository import Gtk


class EqualizerWindow():
    GLADE_FILE = pkg_resources.resource_filename('mokaplayer',
                                                 'data/ui/equalizer_window.ui')

    PROFILES = {
        "Flat (default)": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "Ballad": [4, 3.75, 2.5, 0, -4, -6, -3, 0, 2.5, 9],
        "Boost Bass": [4, 4, 4, 0, 0, 0, 0, 0, 0, 0],
        "Boost Trebble": [0, 0, 0, 0, 0, 0, 0, 4, 4, 4],
        "Boost Bass & Trebble": [4, 4, 4, 0, 0, 0, 0, 4, 4, 4],
        "Classic": [0, 0, 0, 0, 0, 0, -5, -6, -6, -8.5],
        "Dance": [6, 4.5, 1.5, 0, 0, -3.75, -4.5, -4.5, 0, 0],
        "Rock": [4, 3, 2, 1, 0, 0, 1, 2, 3, 4],
        "Soft": [3, 1.125, -0.75, -1.5, -0.75, 1.625, 4.25, 5, 5.75, 6.5],
        "Custom": []
    }

    def __init__(self, streamer: Streamer):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.GLADE_FILE)
        self.builder.connect_signals(self)
        self.window = self.builder.get_object('equlizer_window')
        self.box = self.builder.get_object('box')
        self.cmb_profile = self.builder.get_object('cmb_profile')
        self.streamer = streamer
        self.list_scale = []

        for x in range(0, 10):
            value = self.streamer.get_equalizer_band(x)
            adjustement = Gtk.Adjustment(0, -24, 12, 1, 2, 0)
            adjustement.set_value(value)
            scale = Gtk.Scale()
            scale.set_orientation(Gtk.Orientation.VERTICAL)
            scale.set_adjustment(adjustement)
            scale.set_inverted(True)
            scale.connect('value-changed', self.on_scale_value_changed, x)
            self.box.pack_start(scale, True, True, 0)
            self.list_scale.append(scale)

        self.box.show_all()

        store = Gtk.ListStore(str)
        for x in self.PROFILES:
            store.append([x])

        self.cmb_profile.set_model(store)

    def on_scale_value_changed(self, widget, index):
        self.streamer.set_equalizer_band(index, widget.get_value())
        self.cmb_profile.get_child().set_text("Custom")

    def on_cmb_profile_changed(self, widget):
        profile = self.cmb_profile.get_child().get_text()
        if self.PROFILES[profile]:
            for x in range(0, 10):
                self.streamer.set_equalizer_band(x, self.PROFILES[profile][x])
                self.list_scale[x].set_value(self.PROFILES[profile][x])
        self.cmb_profile.get_child().set_text(profile)

    def get_window(self):
        return self.window
