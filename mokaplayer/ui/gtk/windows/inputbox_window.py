import pkg_resources
from gi.repository import Gtk


class InputBox(Gtk.Dialog):

    def __init__(self, parent, title, text):
        Gtk.Dialog.__init__(self, title, parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(350, 0)
        self.set_default_response(Gtk.ResponseType.OK)

        self.label = Gtk.Label(text)
        self.label.set_margin_start(5)
        self.label.set_margin_top(5)
        self.label.set_margin_bottom(5)
        self.label.set_margin_end(5)

        self.entry = Gtk.Entry()
        self.entry.set_margin_start(5)
        self.entry.set_margin_top(5)
        self.entry.set_margin_bottom(5)
        self.entry.set_margin_end(5)
        self.entry.connect('activate', lambda widget: self.response(Gtk.ResponseType.OK))

        self.get_content_area().add(self.label)
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
