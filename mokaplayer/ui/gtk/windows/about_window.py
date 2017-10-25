import mokaplayer
import pkg_resources
from gi.repository import Gtk


class AboutWindow():
    GLADE_FILE = pkg_resources.resource_filename('mokaplayer',
                                                 'data/ui/about_window.ui')

    @staticmethod
    def get_diaglog():
        builder = Gtk.Builder()
        builder.add_from_file(AboutWindow.GLADE_FILE)
        dialog = builder.get_object('about_dialog')
        dialog.set_version(mokaplayer.__version__)

        return dialog
