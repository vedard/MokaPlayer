from gi.repository import Gtk


class AdapterTab:
    @staticmethod
    def create_row(tab):
        return [
            str(tab['type']),
            tab['name'],
            tab['rating'],
            tab['votes'],
            tab['url']
        ]

    @staticmethod
    def create_store():
        return Gtk.ListStore(str, str, int, int, str)

    @staticmethod
    def create_col_number():
        return [0, 1, 2, 3, 4]
