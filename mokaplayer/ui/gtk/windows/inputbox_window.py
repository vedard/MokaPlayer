import pkg_resources
from gi.repository import Gtk


class InputBox(Gtk.Dialog):

    def __init__(self, parent, text):
        Gtk.Dialog.__init__(self, text, parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)
        self.set_default_response(Gtk.ResponseType.OK)

        self.entry = Gtk.Entry()
        self.entry.connect('activate', lambda: self.response(Gtk.ResponseType.OK))
        self.get_content_area().add(self.entry)

    def get_text(self):
        self.show_all()
        response = self.run()
        text = self.entry.get_text()
        self.destroy()
        if response == Gtk.ResponseType.OK:
            return text
        else:
            return None
