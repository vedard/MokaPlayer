from gi.repository import Gtk


class AboutWindow():

    @staticmethod
    def get_diaglog():
        builder = Gtk.Builder()
        builder.add_from_file('musicplayer/ui/gtk/resources/about_window.ui')
        return builder.get_object('about_dialog')
