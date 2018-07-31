from threading import Thread

import pkg_resources
from gi.repository import GObject, Gtk
from mokaplayer.core.fetchers import tabs as tabs_fetcher
from mokaplayer.ui.gtk.adapter import AdapterTab
from mokaplayer.ui.gtk.helper import file_helper


class TabsWindow():

    GLADE_FILE = pkg_resources.resource_filename('mokaplayer',
                                                 'data/ui/tabs_window.ui')

    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.GLADE_FILE)
        self.builder.connect_signals(self)
        self.window = self.builder.get_object('window')
        self.gridview = self.builder.get_object('gridview')
        self.textview = self.builder.get_object('textview')

    def start_fetch(self, song):
        self.song = song
        self.textview.get_buffer().set_text('')

        if self.song is not None:
            Thread(target=self.fetch).start()
        else:
            self.textview.get_buffer().set_text('')

    def fetch(self):
        result = tabs_fetcher.search(self.song.Title, self.song.Artist)
        model = AdapterTab.create_store()
        for tab in reversed(result):
            model.insert_with_valuesv(0,
                                      AdapterTab.create_col_number(),
                                      AdapterTab.create_row(tab))

        GObject.idle_add(lambda: self.on_fetch_finished(model))

    def on_fetch_finished(self, model):
        self.model = model
        self.gridview.set_model(model)

    def download(self, path):
        text = ''
        tab_type = self.model[path][0]
        name = self.model[path][1]
        url = self.model[path][4]

        if tab_type == 'Tab':
            text = tabs_fetcher.fetch_ascii_tab(url)

        elif tab_type == 'Guitar Pro':
            path = tabs_fetcher.download_guitar_pro_tab(url, '/tmp/')

            if path is not None:
                text = f'{name} downloaded at "{path}"'
                file_helper.open_file(path)
            else:
                text = f'Error while downloading {name}'

        GObject.idle_add(lambda: self.on_download_finished(text))

    def on_download_finished(self, text):
        self.textview.get_buffer().set_text(text)

    def on_gridview_row_activated(self, treeview, path, column):
        Thread(target=lambda: self.download(path)).start()

    def get_window(self):
        return self.window
