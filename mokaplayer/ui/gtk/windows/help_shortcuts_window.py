import pkg_resources
from gi.repository import Gtk


class HelpShortcutsWindow():
    GLADE_FILE = pkg_resources.resource_filename('mokaplayer',
                                                 'data/ui/help_shortcuts_window.ui')

    @staticmethod
    def get_diaglog():
        builder = Gtk.Builder()
        builder.add_from_file(HelpShortcutsWindow.GLADE_FILE)
        return builder.get_object('shortcuts_window')
