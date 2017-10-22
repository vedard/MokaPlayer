import threading
import time
import datetime
import arrow
import logging
import pkg_resources

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Pango
from mokaplayer.core.player import Player
from mokaplayer.core.m3u_parser import M3uParser
from mokaplayer.core.library import Library
from mokaplayer.core.queue import Queue
from mokaplayer.core.helpers import time_helper
from mokaplayer.ui.gtk.helper import image_helper, file_helper
from mokaplayer.ui.gtk.adapter import AdapterSong
from mokaplayer.core.playlists import (AbstractPlaylist, LibraryPlaylist, M3UPlaylist, MostPlayedPlaylist,
                                       RecentlyAddedPlaylist, RecentlyPlayedPlaylist, UpNextPlaylist,
                                       RarelyPlayedPlaylist)
from mokaplayer.ui.gtk.windows import (AboutWindow, LyricsWindow, TabsWindow,
                                       TagsEditorWindow, HelpShortcutsWindow, InputBox)


class MainWindow(Gtk.Window):
    """ Main window
    """

    GLADE_FILE = pkg_resources.resource_filename('mokaplayer',
                                                 'data/ui/main_window.ui')

    def __init__(self, appconfig, userconfig, player):
        super().__init__(title="MokaPlayer", default_width=1366, default_height=768)

        self.logger = logging.getLogger('MainWindow')
        self.appconfig = appconfig
        self.userconfig = userconfig
        self.player = player
        self.current_playlist = LibraryPlaylist()
        self.set_icon_from_file(pkg_resources.resource_filename('mokaplayer', 'data/mokaplayer.png'))

        if self.userconfig['gtk']['darktheme']:
            settings = Gtk.Settings.get_default()
            settings.set_property("gtk-application-prefer-dark-theme", True)

        self.connect("destroy", self.on_window_destroy)
        self.connect("key-press-event", self.on_window_key_press)

        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.GLADE_FILE)
        self.__get_object()
        self.__init_sort_radio()
        self.__init_gridview_columns()
        self.__init_sidebar()

        self.builder.connect_signals(self)
        self.player.state_changed.subscribe(self.on_player_state_changed)
        self.player.audio_changed.subscribe(self.on_audio_changed)
        self.player.volume_changed.subscribe(self.on_volume_changed)

        self.__set_model(AdapterSong.create_store())
        self.__set_current_song_info()
        self.on_volume_changed()

        threading.Thread(target=lambda: self.__create_model()).start()

        GObject.timeout_add(750, self.on_tick, None)
        self.logger.info('Window loaded')

        if not self.player.library.is_musics_folder_valid():
            self.__ask_for_music_folder()

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

    def __create_model(self, order=AbstractPlaylist.OrderBy.DEFAULT, desc=False):
        self.logger.info('Creating ListStore')
        start = time.perf_counter()

        model = AdapterSong.create_store()
        order = AbstractPlaylist.OrderBy[self.userconfig['grid']['sort']['field']]
        desc = self.userconfig['grid']['sort']['desc']
        songs = self.current_playlist.songs(order, desc)

        for row in songs:
            model.insert_with_valuesv(-1, AdapterSong.create_col_number(), AdapterSong.create_row(row))

        end = time.perf_counter()
        self.logger.info('ListStore created in {:.3f} seconds'.format(end - start))

        GObject.idle_add(lambda: self.__set_model(model))

    def __set_model(self, model):
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
        self.menuchild_gridview_playlist = self.builder.get_object('menuchild_gridview_playlist')
        self.listbox_playlist = self.builder.get_object('listbox_playlist')
        self.playlist_sidebar = self.builder.get_object('playlist_sidebar')
        self.lbl_playlist = self.builder.get_object('lbl_playlist')
        self.add(self.content)

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

        self.listbox_playlist.add(self.__create_sidebar_header('Collections'))
        self.listbox_playlist.add(self.__create_sidebar_row(LibraryPlaylist()))
        self.listbox_playlist.add(self.__create_sidebar_row(UpNextPlaylist(self.player.queue)))
        self.listbox_playlist.add(self.__create_sidebar_row(MostPlayedPlaylist()))
        self.listbox_playlist.add(self.__create_sidebar_row(RarelyPlayedPlaylist()))
        self.listbox_playlist.add(self.__create_sidebar_row(RecentlyPlayedPlaylist()))
        self.listbox_playlist.add(self.__create_sidebar_row(RecentlyAddedPlaylist()))
        self.listbox_playlist.add(self.__create_sidebar_header('Playlists'))

        for playlist_location in self.player.library.get_playlists():
            m3u = M3uParser(playlist_location)
            menu_item = Gtk.MenuItem(label=m3u.name)
            menu_item.connect('activate', self.on_menu_gridview_add_to_playlist_activate, m3u)
            self.menuchild_gridview_playlist.append(menu_item)
            self.listbox_playlist.add(self.__create_sidebar_row(M3UPlaylist(m3u)))

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
            self.lbl_current_title.set_text(line1.format(**song._data))
            self.lbl_current_song_infos.set_text(line2.format(**song._data))
        else:
            self.lbl_current_title.set_text('')
            self.lbl_current_song_infos.set_text('')

        self.img_current_album.set_from_pixbuf(image_helper.load(album.Cover if album else None,
                                                                 image_size, image_size))

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

    def on_window_key_press(self, widget, event):
        keyval_name = Gdk.keyval_name(event.keyval)
        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)

        if ctrl and keyval_name == 'f':
            search_mode = self.search_bar.get_search_mode()
            self.search_bar.set_search_mode(not search_mode)
            if not search_mode:
                self.txt_search.grab_focus()
        elif ctrl and keyval_name == 'l':
            self.__show_lyrics(self.player.queue.peek())
        elif ctrl and keyval_name == 'p':
            self.__show_sidebar(not self.playlist_sidebar.get_reveal_child())
        elif ctrl and keyval_name == 'o':
            self.__focus_song(self.player.queue.peek())
        elif ctrl and keyval_name == 'Left':
            self.player.streamer.volume -= 0.05
        elif ctrl and keyval_name == 'Right':
            self.player.streamer.volume += 0.05
        elif keyval_name == "Escape":
            self.search_bar.set_search_mode(False)
        elif keyval_name == "space" and not self.txt_search.has_focus():
            self.player.toggle()
        else:
            return False

        return True

    def on_listbox_playlist_row_activated(self, widget, row):
        self.current_playlist = row.playlist
        self.lbl_playlist.set_text(row.playlist.name)
        threading.Thread(target=lambda: self.__create_model()).start()

    def on_gridview_button_press_event(self, sender, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.menu_gridview.popup(None, None, None, None, event.button, event.time)
            return True

    def on_menu_gridview_append_activate(self, widget):
        self.player.queue.append(self.__get_selected_songs_in_gridview())

    def on_menu_gridview_insert_activate(self, widget):
        self.player.queue.prepend(self.__get_selected_songs_in_gridview())

    def on_menu_gridview_add_to_playlist_activate(self, widget, playlist):
        playlist.read()
        for path in self.__get_selected_songs_in_gridview():
            playlist.append(path)
        playlist.write()

    def on_menu_gridview_replace_activate(self, widget):
        self.player.queue.clear()
        self.player.queue.append(self.__get_selected_songs_in_gridview())

    def on_menu_gridview_edit_activate(self, widget):
        selected_songs = self.__get_selected_songs_in_gridview()
        if any(selected_songs):
            self.__show_tagseditor(selected_songs)

    def on_menu_gridview_tabs_activate(self, widget):
        selected_songs = self.__get_selected_songs_in_gridview()
        if any(selected_songs):
            self.__show_tabs(selected_songs[0])

    def on_menu_gridview_lyrics_activate(self, widget):
        selected_songs = self.__get_selected_songs_in_gridview()
        if any(selected_songs):
            self.__show_lyrics(selected_songs[0])

    def on_menu_gridview_folder_activate(self, widget):
        selected_songs = self.__get_selected_songs_in_gridview()
        if any(selected_songs):
            file_helper.open_folder(selected_songs[0])

    def __get_selected_songs_in_gridview(self):
        model, pathlist = self.gridview.get_selection().get_selected_rows()
        result = []
        for path in pathlist:
            result.append(model[path][0])
        return result

    def on_gridview_row_activated(self, widget, path, column):
        self.player.seek(self.model[path][0])

    def on_btn_next_clicked(self, widget):
        self.player.next()

    def on_btn_play_clicked(self, widget):
        self.player.toggle()
        self.__set_current_play_icon()

    def on_btn_previous_clicked(self, widget):
        self.player.prev()

    def on_audio_changed(self):
        GObject.idle_add(self.__set_current_song_info)
        GObject.idle_add(self.__set_current_play_icon)

    def on_player_state_changed(self):
        GObject.idle_add(self.__set_current_play_icon)

    def on_volume_changed(self):
        self.volume_scale.set_value(self.player.streamer.volume * 100)

    def on_volume_scale_value_changed(self, widget):
        self.player.streamer.volume = self.volume_scale.get_value() / 100

    def on_txt_search_key_press_event(self, widget, event):
        keyval_name = Gdk.keyval_name(event.keyval)
        if keyval_name == "Return" and any(self.model):
            self.__focus_song(self.model[0][0])

    def on_txt_search_search_changed(self, widget):
        self.model.refilter()

    def on_player_open_stream_activate(self, event):
        pass

    def on_player_preferences_activate(self, event):
        pass

    def on_player_quit_activate(self, event):
        Gtk.main_quit()

    def on_library_scan_activate(self, event):
        threading.Thread(target=self.__library_scan).start()

    def on_library_scan_finished(self):
        self.on_sort_radio_toggled(None)
        self.__create_playlist_menus()

    def on_library_artworks_activate(self, event):
        threading.Thread(target=lambda: self.__library_artwork()).start()

    def on_library_artworks_finished(self):
        self.__set_current_song_info()

    def on_queue_add_activate(self, event):
        self.player.queue.clear()
        self.player.queue.append([x.Path for x in LibraryPlaylist().songs()])
        self.player.queue.seek(self.player.queue.pop())

    def on_queue_add_playlist_activate(self, event):
        order = AbstractPlaylist.OrderBy[self.userconfig['grid']['sort']['field']]
        desc = self.userconfig['grid']['sort']['desc']
        self.player.queue.clear()
        self.player.queue.append([x.Path for x in self.current_playlist.songs(order, desc)])

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

    def on_view_toggle_sidebar_activate(self, widget):
        self.__show_sidebar(not self.playlist_sidebar.get_reveal_child())

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
            threading.Thread(target=lambda: self.__create_model()).start()
