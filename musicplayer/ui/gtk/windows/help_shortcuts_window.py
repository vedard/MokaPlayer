from gi.repository import Gtk


class HelpShortcutsWindow():

    @staticmethod
    def get_diaglog():
        builder = Gtk.Builder()
        builder.add_from_file('musicplayer/ui/gtk/resources/help_shortcuts_window.ui')
        return builder.get_object('shortcuts_window')
