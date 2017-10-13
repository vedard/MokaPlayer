import pkg_resources

from gi.repository import Gtk


class AboutWindow():
    GLADE_FILE = pkg_resources.resource_filename('musicplayer',
                                                 'data/ui/about_window.ui')

    @staticmethod
    def get_diaglog():
        builder = Gtk.Builder()
        builder.add_from_file(AboutWindow.GLADE_FILE)
        return builder.get_object('about_dialog')
