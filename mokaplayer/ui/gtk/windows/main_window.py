import logging
import threading
import time

import pkg_resources
from gi.repository import Gdk, GObject, Gtk, Pango
from mokaplayer.core.helpers import time_helper
from mokaplayer.core.database import Artist, Album
from mokaplayer.ui.gtk.adapter import AdapterSong
from mokaplayer.ui.gtk.helper import file_helper, image_helper
from mokaplayer.ui.gtk.controls import AlbumView, ArtistView
from mokaplayer.ui.gtk.windows import (AboutWindow, HelpShortcutsWindow,
                                       InputBox, LyricsWindow, TabsWindow,
                                       TagsEditorWindow, EqualizerWindow,
                                       TempoWindow)
from mokaplayer.core.playlists import (AbstractPlaylist, SongsPlaylist,
                                       M3UPlaylist, MostPlayedPlaylist,
                                       RarelyPlayedPlaylist,
                                       RecentlyAddedPlaylist,
                                       RecentlyPlayedPlaylist, UpNextPlaylist,
                                       AlbumsPlaylist, ArtistsPlaylist,
                                       AlbumPlaylist, ArtistPlaylist)


class MainWindow(Gtk.Window):
    """ Main window
    """

    GLADE_FILE = pkg_resources.resource_filename('mokaplayer', 'data/ui/main_window.ui')
    CSS_FILE = pkg_resources.resource_filename('mokaplayer', 'data/ui/application.css')
    ICON_FILE = pkg_resources.resource_filename('mokaplayer', 'data/icons/hicolor/48x48/apps/mokaplayer.png')

    def __init__(self, appconfig, userconfig, player):
        super().__init__(title="MokaPlayer", default_width=1366, default_height=768)

        self.logger = logging.getLogger('MainWindow')
        self.appconfig = appconfig
        self.userconfig = userconfig
        self.player = player
        self.current_playlist = SongsPlaylist()
        self.set_icon_from_file(self.ICON_FILE)
        self.has_flowbox_album_loaded = False
        self.has_flowbox_artist_loaded = False
        self.is_fullscreen = False

        style_provider = Gtk.CssProvider()
        style_provider.load_from_path(self.CSS_FILE)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        if self.userconfig['gtk']['darktheme']:
            settings = Gtk.Settings.get_default()
            settings.set_property("gtk-application-prefer-dark-theme", True)

        self.connect("destroy", self.on_window_destroy)
        self.connect("key-press-event", self.on_window_key_press)
        self.connect("window-state-event", self.on_window_state_event)

        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.GLADE_FILE)
        self.__get_object()
        self.__init_sort_radio()
        self.__init_gridview_columns()
        self.__init_sidebar()
        self.__init_txt_goto()
        self.__init_cmb_visualiser()

        self.builder.connect_signals(self)
        self.player.state_changed.subscribe(self.on_player_state_changed)
        self.player.audio_changed.subscribe(self.on_audio_changed)
        self.player.volume_changed.subscribe(self.on_volume_changed)

        self.__set_current_song_info()
        self.on_volume_changed()

        self.__show_current_playlist()

        GObject.timeout_add(750, self.on_tick, None)
        self.logger.info('Window loaded')

        if not self.player.library.is_musics_folder_valid():
            self.__ask_for_music_folder()

    def on_visualizer_realize(self, data):
        self.player.streamer.draw_on(self.visualizer.get_property('window').get_xid())

    def on_visualizer_draw(self, widget, data):
        allocation = widget.get_allocation()
        data.set_source_rgb(0, 0, 0)
        data.rectangle(0, 0, allocation.width, allocation.height)
        data.fill()
        return False

    def __ask_for_music_folder(self):
        dialog = Gtk.FileChooserDialog("Select where is your music", self,
                                       Gtk.FileChooserAction.SELECT_FOLDER,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        "Select", Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.player.library.musics_folder = dialog.get_filename()
            self.on_library_scan_activate(None)
        dialog.destroy()

    def __manage_goto(self):
        p = self.player.library.get_playlist(self.txt_goto.get_text())
        if p:
            self.current_playlist = p
            self.__show_current_playlist()
            self.goto_bar.set_search_mode(False)
            GObject.idle_add(lambda: self.txt_goto.set_text(''))

    def __init_txt_goto(self):
        completion = Gtk.EntryCompletion()
        store = Gtk.ListStore(str)

        artists_name = {x.Name for x in ArtistsPlaylist().collections()}
        albums_name = {x.Name for x in AlbumsPlaylist().collections()}

        for x in artists_name.union(albums_name):
            store.append([x])

        completion.set_model(store)
        completion.set_text_column(0)
        completion.set_inline_completion(True)
        completion.set_match_func(self.__txt_goto_match_func)
        completion.set_inline_selection(True)
        completion.connect('match_selected', lambda x, y, z: self.__manage_goto())
        self.txt_goto.set_completion(completion)

    def __txt_goto_match_func(self, completion, key_string, iter):
        modelstr = completion.get_model()[iter][0].lower()
        return key_string.lower() in modelstr

    def __init_cmb_visualiser(self):
        store = Gtk.ListStore(str)
        for x in self.player.streamer.Visualizers:
            store.append([x])

        self.cmb_visualiser.set_model(store)

    def __init_gridview_columns(self):
        columns = self.gridview.get_columns()
        font = self.userconfig['grid']['font']
        for col in columns:
            col.set_visible(False)

            if font:
                for cell in col.get_cells():
                    cell.set_property('font', font)

        for name in reversed(self.userconfig['grid']['columns']):
            for col in columns:
                if name == col.get_title():
                    col.set_visible(True)
                    self.gridview.move_column_after(col, None)

    def __create_model(self):
        self.logger.info('Creating ListStore')
        start = time.perf_counter()

        model = AdapterSong.create_store()
        order = AbstractPlaylist.OrderBy[self.userconfig['grid']['sort']['field']]
        desc = self.userconfig['grid']['sort']['desc']
        songs = self.current_playlist.collections(order, desc)

        for row in songs:
            model.insert_with_valuesv(-1, AdapterSong.create_col_number(), AdapterSong.create_row(row))

        GObject.idle_add(lambda: self.__create_model_finished(model))

        end = time.perf_counter()
        self.logger.info('ListStore created in {:.3f} seconds'.format(end - start))

    def __create_model_finished(self, model):
        self.model = model.filter_new()
        self.model.set_visible_func(self.__model_filter_func)
        self.gridview.set_model(self.model)

    def __get_object(self):
        self.content = self.builder.get_object('content')
        self.gridview = self.builder.get_object('gridview')
        self.col_added = self.builder.get_object('col_added')
        self.col_length = self.builder.get_object('col_length')
        self.lbl_current_title = self.builder.get_object('lbl_current_title')
        self.lbl_current_song_infos = self.builder.get_object('lbl_current_song_infos')
        self.volume_scale = self.builder.get_object('volume_scale')
        self.btn_previous = self.builder.get_object('btn_previous')
        self.btn_play = self.builder.get_object('btn_play')
        self.btn_next = self.builder.get_object('btn_next')
        self.img_current_album = self.builder.get_object('img_current_album')
        self.img_play = self.builder.get_object('img_play')
        self.img_pause = self.builder.get_object('img_pause')
        self.txt_search = self.builder.get_object('txt_search')
        self.txt_goto = self.builder.get_object('txt_goto')
        self.lbl_current_time = self.builder.get_object('lbl_current_time')
        self.prb_current_time = self.builder.get_object('prb_current_time')
        self.radio_sort_artist = self.builder.get_object('radio_sort_artist')
        self.radio_sort_album = self.builder.get_object('radio_sort_album')
        self.radio_sort_title = self.builder.get_object('radio_sort_title')
        self.radio_sort_year = self.builder.get_object('radio_sort_year')
        self.radio_sort_length = self.builder.get_object('radio_sort_length')
        self.radio_sort_added = self.builder.get_object('radio_sort_added')
        self.radio_sort_played = self.builder.get_object('radio_sort_played')
        self.radio_sort_default = self.builder.get_object('radio_sort_default')
        self.chk_sort_desc = self.builder.get_object('chk_sort_desc')
        self.menu_gridview = self.builder.get_object('menu_gridview')
        self.search_bar = self.builder.get_object('search_bar')
        self.goto_bar = self.builder.get_object('goto_bar')
        self.menuchild_gridview_playlist = self.builder.get_object('menuchild_gridview_playlist')
        self.menu_gridview_remove_from_playlist = self.builder.get_object('menu_gridview_remove_from_playlist')
        self.listbox_playlist = self.builder.get_object('listbox_playlist')
        self.playlist_sidebar = self.builder.get_object('playlist_sidebar')
        self.playlist_buttons = self.builder.get_object('playlist_buttons')
        self.lbl_playlist = self.builder.get_object('lbl_playlist')
        self.flowbox_artist = self.builder.get_object('flowbox_artist')
        self.flowbox_album = self.builder.get_object('flowbox_album')
        self.stack = self.builder.get_object('stack')
        self.album_viewport = self.builder.get_object('album_viewport')
        self.visualizer = self.builder.get_object('visualizer')
        self.cmb_visualiser = self.builder.get_object('cmb_visualiser')
        self.box_view_title = self.builder.get_object('box_view_title')
        self.add(self.content)

    def __show_current_playlist(self):
        if self.is_visualizer_on():
            self.turn_visualizer_off()

        self.lbl_playlist.set_text(self.current_playlist.name)
        if isinstance(self.current_playlist, AlbumPlaylist):
            for child in self.album_viewport.get_children():
                self.album_viewport.remove(child)
            self.stack.set_visible_child_name('album_view')
            self.album_viewport.add(AlbumView(self.current_playlist,
                                              self.on_gridview_row_activated,
                                              self.on_gridview_button_press_event,
                                              hide_header=True).get_view())

        elif isinstance(self.current_playlist, ArtistPlaylist):
            for child in self.album_viewport.get_children():
                self.album_viewport.remove(child)
            self.stack.set_visible_child_name('album_view')
            self.album_viewport.add(ArtistView(self.current_playlist,
                                               self.on_gridview_row_activated,
                                               self.on_gridview_button_press_event).get_view())

        elif isinstance(self.current_playlist, AlbumsPlaylist):
            self.stack.set_visible_child_name('flowbox_album')
            self.flowbox_album.unselect_all()
            if not self.has_flowbox_album_loaded:
                self.__create_flowbox(self.flowbox_album)
                self.has_flowbox_album_loaded = True

        elif isinstance(self.current_playlist, ArtistsPlaylist):
            self.stack.set_visible_child_name('flowbox_artist')
            self.flowbox_artist.unselect_all()
            if not self.has_flowbox_artist_loaded:
                self.__create_flowbox(self.flowbox_artist)
                self.has_flowbox_artist_loaded = True
        else:
            self.gridview.set_model(AdapterSong.create_store())
            self.stack.set_visible_child_name('gridview')
            threading.Thread(target=self.__create_model).start()

        if isinstance(self.current_playlist, UpNextPlaylist):
            self.playlist_buttons.set_visible(False)
        else:
            self.playlist_buttons.set_visible(True)

    def __create_flowbox(self, flowbox):
        self.logger.info('Creating Flowbox')
        start = time.perf_counter()

        image_loading_queue = []
        children = []

        order = AbstractPlaylist.OrderBy[self.userconfig['grid']['sort']['field']]
        desc = self.userconfig['grid']['sort']['desc']
        image_size = self.userconfig['flowbox']['image_size']
        margin = self.userconfig['flowbox']['margin']
        collections = self.current_playlist.collections(order, desc, self.txt_search.get_text())

        for child in flowbox.get_children():
            flowbox.remove(child)

        for item in collections:
            image = Gtk.Image()
            image.set_size_request(image_size, image_size)
            image.get_style_context().add_class('cover')
            image_loading_queue.append((image, item.Cover, image_size, image_size))

            if isinstance(item, Album):
                children.append(self.__create_album_flowboxitem(item, image, margin))
            elif isinstance(item, Artist):
                children.append(self.__create_artist_flowboxitem(item, image, margin))

        for child in children:
            flowbox.add(child)
        flowbox.show_all()

        image_helper.set_multiple_image(image_loading_queue)

        end = time.perf_counter()
        self.logger.info('Flowbox created in {:.3f} seconds'.format(end - start))

    def __create_artist_flowboxitem(self, artist, image, margin):
        label_album = Gtk.Label(artist.Name, max_width_chars=0, justify=Gtk.Justification.LEFT,
                                ellipsize=Pango.EllipsizeMode.END, xalign=0, margin_top=5)
        label_album.get_style_context().add_class('text110')

        flowboxchild = Gtk.FlowBoxChild()
        grid = Gtk.Grid(margin=margin, halign=Gtk.Align.CENTER)
        grid.attach(image, 0, 0, 1, 1)
        grid.attach(label_album, 0, 1, 1, 1)
        flowboxchild.add(grid)
        flowboxchild.data = artist
        return flowboxchild

    def __create_album_flowboxitem(self, album, image, margin):
        label_album = Gtk.Label(f'{album.Name} ({album.Year})', max_width_chars=0,
                                justify=Gtk.Justification.LEFT, wrap=True,
                                wrap_mode=Pango.WrapMode.WORD_CHAR, xalign=0, margin_top=5)
        label_artist = Gtk.Label(album.Artist, max_width_chars=0, justify=Gtk.Justification.LEFT,
                                 ellipsize=Pango.EllipsizeMode.END, xalign=0, margin_top=5)

        label_album.get_style_context().add_class('text110')
        label_artist.get_style_context().add_class('dim-label')
        flowboxchild = Gtk.FlowBoxChild(halign=Gtk.Align.CENTER)
        grid = Gtk.Grid(margin=margin, halign=Gtk.Align.CENTER)
        grid.attach(image, 0, 0, 1, 1)
        grid.attach(label_album, 0, 1, 1, 1)
        grid.attach(label_artist, 0, 2, 1, 1)
        flowboxchild.add(grid)
        flowboxchild.data = album
        return flowboxchild

    def __create_sidebar_row(self, playlist):
        list_box_row = Gtk.ListBoxRow()
        list_box_row.playlist = playlist
        list_box_row.set_size_request(0, 40)
        list_box_row.add(Gtk.Label(playlist.name, margin_left=20, halign=Gtk.Align.START))
        return list_box_row

    def __create_sidebar_header(self, name):
        list_box_row = Gtk.ListBoxRow(activatable=False, selectable=False)
        list_box_row.set_size_request(0, 40)
        label = Gtk.Label(f'<b>{name}</b>', margin_left=10, halign=Gtk.Align.START, use_markup=True)
        list_box_row.add(label)
        return list_box_row

    def __create_playlist_menus(self):
        for child in self.menuchild_gridview_playlist.get_children():
            self.menuchild_gridview_playlist.remove(child)

        for child in self.listbox_playlist.get_children():
            self.listbox_playlist.remove(child)

        self.listbox_playlist.add(self.__create_sidebar_header('Library'))
        self.listbox_playlist.add(self.__create_sidebar_row(SongsPlaylist()))
        self.listbox_playlist.add(self.__create_sidebar_row(AlbumsPlaylist()))
        self.listbox_playlist.add(self.__create_sidebar_row(ArtistsPlaylist()))
        self.listbox_playlist.add(self.__create_sidebar_row(UpNextPlaylist(self.player.queue)))
        self.listbox_playlist.add(self.__create_sidebar_row(MostPlayedPlaylist()))
        self.listbox_playlist.add(self.__create_sidebar_row(RarelyPlayedPlaylist()))
        self.listbox_playlist.add(self.__create_sidebar_row(RecentlyPlayedPlaylist()))
        self.listbox_playlist.add(self.__create_sidebar_row(RecentlyAddedPlaylist()))
        self.listbox_playlist.add(self.__create_sidebar_header('Playlists'))

        for playlist in self.player.library.get_playlists():
            menu_item = Gtk.MenuItem(label=playlist.name)
            menu_item.connect('activate', self.on_menu_gridview_add_to_playlist_activate,
                              playlist, self.menu_gridview)
            self.menuchild_gridview_playlist.append(menu_item)
            self.listbox_playlist.add(self.__create_sidebar_row(playlist))

        self.menuchild_gridview_playlist.show_all()
        self.listbox_playlist.show_all()

    def __set_current_song_info(self):
        self.logger.debug("Setting currrent song info")
        image_size = self.userconfig['header']['image_size']
        line1 = self.userconfig['header']['line1']
        line2 = self.userconfig['header']['line2']

        song = self.player.library.get_song(self.player.queue.peek())
        album = None

        if song:
            album = self.player.library.get_album(song.Album, song.AlbumArtist)
            self.lbl_current_title.set_text(line1.format(**song.__data__))
            self.lbl_current_song_infos.set_text(line2.format(**song.__data__))
        else:
            self.lbl_current_title.set_text('')
            self.lbl_current_song_infos.set_text('')

        args = (self.img_current_album, album.Cover if album else None, image_size, image_size)
        threading.Thread(target=image_helper.set_image, args=args).start()

    def __set_current_play_icon(self):
        if self.player.streamer.state == self.player.streamer.State.PLAYING:
            self.btn_play.set_image(self.img_pause)
        else:
            self.btn_play.set_image(self.img_play)

    def __model_filter_func(self, model, iter, data):
        return AdapterSong.search(self.txt_search.get_text(), model[iter])

    def __focus_song(self, path):
        for row in self.model:
            if row[0] == path:
                self.gridview.get_selection().select_path(row.path)
                self.gridview.set_cursor(row.path)
                self.gridview.scroll_to_cell(row.path, use_align=True)
                self.gridview.grab_focus()
                break

    def __show_lyrics(self, path):
        song = self.player.library.get_song(path)
        w = LyricsWindow()
        w.start_fetch(song)
        w.get_window().set_transient_for(self)
        w.get_window().show()

    def __show_tabs(self, path):
        song = self.player.library.get_song(path)
        w = TabsWindow()
        w.start_fetch(song)
        w.get_window().set_transient_for(self)
        w.get_window().show()

    def __show_tagseditor(self, paths):
        songs = list(self.player.library.get_songs(paths))
        w = TagsEditorWindow(songs)
        w.get_window().set_transient_for(self)
        w.get_window().show()

    def __library_scan(self):
        self.player.library.sync()
        GObject.idle_add(self.on_library_scan_finished)

    def __library_artwork(self):
        self.player.library.sync_artwork()
        GObject.idle_add(self.on_library_artworks_finished)

    def on_window_destroy(self, widget):
        self.player.save()
        Gtk.main_quit()

    def on_window_state_event(self, widget, event):
        self.is_fullscreen = bool(event.new_window_state & Gdk.WindowState.FULLSCREEN)

    def on_window_key_press(self, widget, event):
        keyval_name = Gdk.keyval_name(event.keyval)
        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)

        if ctrl and keyval_name == 'f':
            search_mode = self.search_bar.get_search_mode()
            self.search_bar.set_search_mode(not search_mode)
            if not search_mode:
                self.txt_search.grab_focus()
                self.goto_bar.set_search_mode(False)
        elif ctrl and keyval_name == 'l':
            self.__show_lyrics(self.player.queue.peek())
        elif ctrl and keyval_name == 'p':
            search_mode = self.goto_bar.get_search_mode()
            self.goto_bar.set_search_mode(not search_mode)
            if not search_mode:
                self.txt_goto.grab_focus()
                self.search_bar.set_search_mode(False)
        elif ctrl and keyval_name == 'o':
            self.__focus_song(self.player.queue.peek())
        elif ctrl and keyval_name == 'y':
            self.on_view_toggle_visualization_activate(None)
        elif ctrl and keyval_name == 'g':
            if self.player.queue.peek():
                self.current_playlist = ArtistPlaylist(song_path=self.player.queue.peek())
                self.__show_current_playlist()
        elif ctrl and keyval_name == 'Left':
            self.player.streamer.volume -= 0.05
        elif ctrl and keyval_name == 'Right':
            self.player.streamer.volume += 0.05
        elif keyval_name == "Escape":
            self.txt_search.set_text('')
            self.txt_goto.set_text('')
            self.search_bar.set_search_mode(False)
            self.goto_bar.set_search_mode(False)
        elif keyval_name == "space" and not self.txt_search.has_focus():
            self.player.toggle()
        elif keyval_name == "F11":
            self.toggle_fullscreen()
        else:
            return False

        return True

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.unfullscreen()
        else:
            self.fullscreen()

    def on_listbox_playlist_row_activated(self, widget, row):
        self.current_playlist = row.playlist
        self.__show_current_playlist()

    def on_gridview_row_activated(self, widget, path, column):
        self.player.seek(widget.get_model()[path][0])

    def on_gridview_button_press_event(self, sender, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            # if its a m3uPlaylist, offer option to remove selected songs
            self.menu_gridview_remove_from_playlist.set_visible(isinstance(self.current_playlist, M3UPlaylist))
            self.menu_gridview.popup(None, None, None, sender, event.button, event.time)
            self.menu_gridview.sender = sender
            return True

    def on_menu_gridview_append_activate(self, widget):
        treeview = widget.get_parent().sender
        self.player.queue.append(self.__get_selected_songs(treeview))

    def on_menu_gridview_insert_activate(self, widget):
        treeview = widget.get_parent().sender
        self.player.queue.prepend(self.__get_selected_songs(treeview))

    def on_menu_gridview_add_to_playlist_activate(self, widget, playlist, menu):
        treeview = menu.sender
        playlist.parser.read()
        for path in self.__get_selected_songs(treeview):
            playlist.parser.append(path)
        playlist.parser.write()

    def on_menu_gridview_remove_from_playlist_activate(self, widget):
        treeview = widget.get_parent().sender
        if isinstance(self.current_playlist, M3UPlaylist):
            self.current_playlist.parser.read()
            for path in self.__get_selected_songs(treeview):
                self.current_playlist.parser.remove(path)
            self.current_playlist.parser.write()
            self.__show_current_playlist()

    def on_menu_gridview_replace_activate(self, widget):
        treeview = widget.get_parent().sender
        self.player.queue.clear()
        self.player.queue.append(self.__get_selected_songs(treeview))

    def on_menu_gridview_edit_activate(self, widget):
        treeview = widget.get_parent().sender
        selected_songs = self.__get_selected_songs(treeview)
        if any(selected_songs):
            self.__show_tagseditor(selected_songs)

    def on_menu_gridview_tabs_activate(self, widget):
        treeview = widget.get_parent().sender
        selected_songs = self.__get_selected_songs(treeview)
        if any(selected_songs):
            self.__show_tabs(selected_songs[0])

    def on_menu_gridview_lyrics_activate(self, widget):
        treeview = widget.get_parent().sender
        selected_songs = self.__get_selected_songs(treeview)
        if any(selected_songs):
            self.__show_lyrics(selected_songs[0])

    def on_menu_gridview_folder_activate(self, widget):
        treeview = widget.get_parent().sender
        selected_songs = self.__get_selected_songs(treeview)
        if any(selected_songs):
            file_helper.open_folder(selected_songs[0])

    def on_menu_gridview_goto_artist_activate(self, widget):
        treeview = widget.get_parent().sender
        selected_songs = self.__get_selected_songs(treeview)
        if any(selected_songs):
            self.current_playlist = ArtistPlaylist(None, song_path=selected_songs[0])
            self.__show_current_playlist()

    def on_menu_gridview_goto_album_activate(self, widget):
        treeview = widget.get_parent().sender
        selected_songs = self.__get_selected_songs(treeview)
        if any(selected_songs):
            self.current_playlist = AlbumPlaylist(None, song_path=selected_songs[0])
            self.__show_current_playlist()

    def __get_selected_songs(self, gridview):
        model, pathlist = gridview.get_selection().get_selected_rows()
        result = []
        for path in pathlist:
            result.append(model[path][0])
        return result

    def on_btn_next_clicked(self, widget):
        self.player.next()

    def on_btn_play_clicked(self, widget):
        self.player.toggle()
        self.__set_current_play_icon()

    def on_btn_previous_clicked(self, widget):
        self.player.prev()

    def on_btn_shuffle_playlist_clicked(self, widget):
        try:
            order = AbstractPlaylist.OrderBy[self.userconfig['grid']['sort']['field']]
            desc = self.userconfig['grid']['sort']['desc']
            self.player.queue.clear()
            self.player.queue.append([x.Path for x in self.current_playlist.collections(order, desc)])
            self.player.queue.shuffle()
            self.player.next()
        except AttributeError:
            pass  # Not all playlist contain songs

    def on_btn_start_playlist_clicked(self, widget):
        try:
            order = AbstractPlaylist.OrderBy[self.userconfig['grid']['sort']['field']]
            desc = self.userconfig['grid']['sort']['desc']
            self.player.queue.clear()
            self.player.queue.append([x.Path for x in self.current_playlist.collections(order, desc)])
            self.player.next()
        except AttributeError:
            pass  # Not all playlist contain songs

    def on_audio_changed(self):
        GObject.idle_add(self.__set_current_song_info)
        GObject.idle_add(self.__set_current_play_icon)

    def on_player_state_changed(self):
        GObject.idle_add(self.__set_current_play_icon)

    def on_volume_changed(self):
        self.volume_scale.set_value(self.player.streamer.volume * 100)

    def on_volume_scale_value_changed(self, widget):
        self.player.streamer.volume = self.volume_scale.get_value() / 100

    def on_txt_goto_key_press_event(self, wiget, event):
        keyval_name = Gdk.keyval_name(event.keyval)
        if keyval_name == "Return":
            self.__manage_goto()

    def on_txt_search_key_press_event(self, widget, event):
        keyval_name = Gdk.keyval_name(event.keyval)
        if keyval_name == "Return" and any(self.model):
            self.__focus_song(self.model[0][0])

    def on_txt_search_search_changed(self, widget):
        self.model.refilter()
        text_len = len(self.txt_search.get_text())
        if text_len == 0 or text_len > 2:
            self.has_flowbox_artist_loaded = False
            self.has_flowbox_album_loaded = False
            if isinstance(self.current_playlist, ArtistsPlaylist):
                self.__show_current_playlist()
            elif isinstance(self.current_playlist, AlbumsPlaylist):
                self.__show_current_playlist()

    def on_tools_equalizer_activate(self, event):
        w = EqualizerWindow(self.player.streamer)
        w.get_window().set_transient_for(self)
        w.get_window().show()

    def on_tools_speed_activate(self, event):
        w = TempoWindow(self.player.streamer)
        w.get_window().set_transient_for(self)
        w.get_window().show()

    def on_player_open_stream_activate(self, event):
        pass

    def on_player_preferences_activate(self, event):
        pass

    def on_player_quit_activate(self, event):
        Gtk.main_quit()

    def on_library_scan_activate(self, event):
        threading.Thread(target=self.__library_scan).start()

    def on_library_scan_finished(self):
        self.__create_playlist_menus()
        self.has_flowbox_album_loaded = False
        self.has_flowbox_artist_loaded = False
        self.__show_current_playlist()

    def on_library_artworks_activate(self, event):
        threading.Thread(target=lambda: self.__library_artwork()).start()

    def on_library_artworks_finished(self):
        self.__set_current_song_info()
        self.has_flowbox_album_loaded = False
        self.has_flowbox_artist_loaded = False
        self.__show_current_playlist()

    def on_queue_add_activate(self, event):
        self.player.queue.clear()
        self.player.queue.append([x.Path for x in SongsPlaylist().collections()])
        self.player.queue.seek(self.player.queue.pop())

    def on_queue_add_playlist_activate(self, event):
        try:
            order = AbstractPlaylist.OrderBy[self.userconfig['grid']['sort']['field']]
            desc = self.userconfig['grid']['sort']['desc']
            self.player.queue.clear()
            self.player.queue.append([x.Path for x in self.current_playlist.collections(order, desc)])
        except AttributeError:
            pass  # Not all playlist contain songs

    def on_queue_clear_activate(self, event):
        self.player.queue.clear()

    def on_queue_shuffle_activate(self, event):
        self.player.queue.shuffle()

    def on_help_shortcuts_activate(self, event):
        shortcuts_window = HelpShortcutsWindow.get_diaglog()
        shortcuts_window.set_transient_for(self)
        shortcuts_window.show()

    def on_help_about_activate(self, event):
        about_window = AboutWindow.get_diaglog()
        about_window.set_transient_for(self)
        about_window.show()

    def on_playlist_create_activate(self, event):
        name = InputBox(self, "Playlist", 'What the name of the playlist?').get_text()
        if name:
            self.player.library.create_playlist(name)
            self.__create_playlist_menus()

    def on_view_toggle_search_activate(self, widget):
        self.search_bar.set_search_mode(not self.search_bar.get_search_mode())
        self.goto_bar.set_search_mode(False)

    def on_view_toggle_sidebar_activate(self, widget):
        self.__show_sidebar(not self.playlist_sidebar.get_reveal_child())

    def on_view_toggle_fullscreen_activate(self, widget):
        self.toggle_fullscreen()

    def on_view_toggle_visualization_activate(self, Widget):
        if self.is_visualizer_on():
            self.turn_visualizer_off()
        else:
            self.turn_visualizer_on()

    def is_visualizer_on(self):
        return self.stack.get_visible_child_name() == 'visualizer'

    def turn_visualizer_on(self):
        self.box_view_title.set_visible(False)
        self.stack.set_visible_child_name('visualizer')
        self.player.streamer.visualizer = self.cmb_visualiser.get_child().get_text()

    def turn_visualizer_off(self):
        self.stack.set_visible_child_name('gridview')
        self.box_view_title.set_visible(True)
        self.player.streamer.visualizer = None

    def on_cmb_visualiser_changed(self, widget):
        self.player.streamer.visualizer = self.cmb_visualiser.get_child().get_text()

    def on_prp_current_time_click(self, widget, event):
        width = self.prb_current_time.get_allocated_width()
        duration = self.player.streamer.duration
        self.player.streamer.position = duration * event.x / width

    def on_tick(self, data):
        position = self.player.streamer.position
        duration = self.player.streamer.duration
        fraction = position / duration if duration else 0
        position_text = time_helper.seconds_to_string(position)
        duration_text = time_helper.seconds_to_string(duration)

        self.lbl_current_time.set_text(f'{position_text} / {duration_text}')
        self.prb_current_time.set_fraction(fraction)

        return True

    def __init_sidebar(self):
        show_sidebar = self.userconfig['sidebar']['show']
        self.__create_playlist_menus()
        if show_sidebar:
            self.playlist_sidebar.set_reveal_child(show_sidebar)

    def __show_sidebar(self, is_visible):
        self.playlist_sidebar.set_reveal_child(is_visible)
        self.userconfig['sidebar']['show'] = is_visible
        threading.Thread(target=self.userconfig.save).start()

    def __init_sort_radio(self):
        order = AbstractPlaylist.OrderBy[self.userconfig['grid']['sort']['field']]
        desc = self.userconfig['grid']['sort']['desc']

        self.chk_sort_desc.set_active(desc)
        if order == AbstractPlaylist.OrderBy.ARTIST:
            self.radio_sort_artist.set_active(True)
        elif order == AbstractPlaylist.OrderBy.ALBUM:
            self.radio_sort_album.set_active(True)
        elif order == AbstractPlaylist.OrderBy.TITLE:
            self.radio_sort_title.set_active(True)
        elif order == AbstractPlaylist.OrderBy.LENGTH:
            self.radio_sort_length.set_active(True)
        elif order == AbstractPlaylist.OrderBy.YEAR:
            self.radio_sort_year.set_active(True)
        elif order == AbstractPlaylist.OrderBy.ADDED:
            self.radio_sort_added.set_active(True)
        elif order == AbstractPlaylist.OrderBy.PLAYED:
            self.radio_sort_played.set_active(True)
        else:
            self.radio_sort_default.set_active(True)

    def on_sort_radio_toggled(self, widget):
        if widget is None or widget.get_active() or not isinstance(widget, Gtk.RadioButton):
            order = AbstractPlaylist.OrderBy.DEFAULT

            if self.radio_sort_default.get_active():
                order = AbstractPlaylist.OrderBy.DEFAULT
            elif self.radio_sort_artist.get_active():
                order = AbstractPlaylist.OrderBy.ARTIST
            elif self.radio_sort_album.get_active():
                order = AbstractPlaylist.OrderBy.ALBUM
            elif self.radio_sort_title.get_active():
                order = AbstractPlaylist.OrderBy.TITLE
            elif self.radio_sort_length.get_active():
                order = AbstractPlaylist.OrderBy.LENGTH
            elif self.radio_sort_year.get_active():
                order = AbstractPlaylist.OrderBy.YEAR
            elif self.radio_sort_added.get_active():
                order = AbstractPlaylist.OrderBy.ADDED
            elif self.radio_sort_played.get_active():
                order = AbstractPlaylist.OrderBy.PLAYED

            self.userconfig['grid']['sort']['desc'] = self.chk_sort_desc.get_active()
            self.userconfig['grid']['sort']['field'] = order.name

            threading.Thread(target=self.userconfig.save).start()
            self.has_flowbox_album_loaded = False
            self.has_flowbox_artist_loaded = False
            self.__show_current_playlist()

    def on_flowbox_selected_children_changed(self, widget):
        selected = widget.get_selected_children()
        if any(selected):
            if isinstance(selected[0].data, Album):
                self.current_playlist = AlbumPlaylist(selected[0].data)
            elif isinstance(selected[0].data, Artist):
                self.current_playlist = ArtistPlaylist(selected[0].data)

            self.__show_current_playlist()
