import threading
import time
import datetime
import arrow
import signal

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from musicplayer.core.player import Player
from musicplayer.ui.gtk.adapter_song import AdapterSong
from musicplayer.ui.gtk.about_window import AboutWindow
from musicplayer.ui.gtk.lyrics_window import LyricsWindow
from musicplayer.ui.gtk.tabs_window import TabsWindow
from musicplayer.ui.gtk.tagseditor_window import TagsEditorWindow
from musicplayer.ui.gtk.help_shortcuts_window import HelpShortcutsWindow
from musicplayer.ui.gtk import image_helper
from musicplayer.ui.gtk import file_helper

class MainWindow(Gtk.Window):
    """ Fenetre principale de l'application
    """
    def __init__(self, appconfig, userconfig):
        Gtk.Window.__init__(self, title="Music Player", default_width=1366, default_height=768)
        
        self.appconfig = appconfig
        self.userconfig = userconfig
        
        self.connect("destroy", self.on_window_destroy)
        self.connect("key-press-event", self.on_window_key_press)
        signal.signal(signal.SIGTERM, self.on_SIGTERM)
        signal.signal(signal.SIGHUP, self.on_SIGTERM)
        signal.signal(signal.SIGINT, self.on_SIGTERM)
        signal.signal(signal.SIGQUIT, self.on_SIGTERM)
        
        self.builder = Gtk.Builder()
        self.builder.add_from_file('musicplayer/ui/gtk/resources/main_window.ui')
        self.builder.connect_signals(self)
        
        self.__get_object()

        self.player = Player(self.appconfig,
                             self.userconfig,
                             self.on_audio_changed, 
                             self.on_volume_changed,
                             self.on_player_state_changed)
        self.player.restore()

        self.__set_model(AdapterSong.create_store())
        self.__set_current_song_info()

        threading.Thread(target=lambda:self.player.restore()).start()
        threading.Thread(target=lambda:self.__create_model(self.player.library.search_song())).start()

        GObject.timeout_add(500, self.on_tick, None)
 
    def __create_model(self, data):
        model = AdapterSong.create_store()
        start = time.perf_counter()

        for row in reversed(data):
            model.insert_with_valuesv(0, 
                                      AdapterSong.create_col_number(),
                                      AdapterSong.create_row(row))

        end = time.perf_counter()
        print(end - start)

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
        self.chk_sort_desc = self.builder.get_object('chk_sort_desc')
        self.menu_gridview = self.builder.get_object('menu_gridview')
        self.add(self.content)
    
    def __set_current_song_info(self):
        song = self.player.library.get_song(self.player.queue.peek())
        album = None

        if song:
            album = self.player.library.get_album(song.Album)
            self.lbl_current_title.set_text(song.Title)
            self.lbl_current_song_infos.set_text(f'{song.Artist} - {song.Album} ({song.Year})')
        elif self.player.queue.peek():
            self.lbl_current_title.set_text('')
            self.lbl_current_song_infos.set_text('(Not in library)')
        else:
            self.lbl_current_title.set_text('')
            self.lbl_current_song_infos.set_text('')

        if album:
            self.img_current_album.set_from_pixbuf(image_helper.load(album.Cover, 128, 128))
        else:
            self.img_current_album.set_from_pixbuf(image_helper.load(None, 128, 128))
        
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
        songs = self.player.library.get_songs(paths)
        w = TagsEditorWindow(songs)
        w.get_window().show()

    def __library_scan(self):
        self.player.library.sync()
        GObject.idle_add(self.on_library_scan_finished)

    def on_SIGTERM(self, signum, frame):
        self.player.save()
        Gtk.main_quit()

    def on_window_destroy(self, widget):
        self.player.save()
        Gtk.main_quit()
    
    def on_window_key_press(self, widget, event):
        keyval_name = Gdk.keyval_name(event.keyval)
        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)

        if ctrl and keyval_name == 'f':
            self.txt_search.grab_focus()
        elif ctrl and keyval_name == 'l':
            self.__show_lyrics(self.player.queue.peek())
        elif ctrl and keyval_name == 'o':
            self.__focus_song(self.player.queue.peek())
        elif ctrl and keyval_name == 'Left':
            self.player.streamer.volume -= 0.05
        elif ctrl and keyval_name == 'Right':
            self.player.streamer.volume += 0.05
        else:
            return False

        return True

    def on_gridview_button_press_event(self, sender, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.menu_gridview.popup( None, None, None, None, event.button, event.time)
            return True
    
    def on_menu_gridview_append_activate(self, widget):
        self.player.queue.append(self.__get_selected_songs_in_gridview())

    def on_menu_gridview_insert_activate(self, widget):
        self.player.queue.prepend(self.__get_selected_songs_in_gridview())

    def on_menu_gridview_replace_activate(self, widget):
        self.player.queue.clear()
        self.player.queue.append(self.__get_selected_songs_in_gridview())

    def on_menu_gridview_edit_activate(self, widget):
        selected_songs = self.__get_selected_songs_in_gridview()
        if any(selected_songs):
            self.__show_tagseditor(self.__get_selected_songs_in_gridview())

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
    
    def on_audio_changed(self, data):
        GObject.idle_add(self.__set_current_song_info)
        GObject.idle_add(self.__set_current_play_icon)
    
    def on_player_state_changed(self):
        GObject.idle_add(self.__set_current_play_icon)

    def on_volume_changed(self, data1, data2):
        self.volume_scale.set_value(self.player.streamer.volume * 100)
    
    def on_volume_scale_value_changed(self, widget):
        self.player.streamer.volume = self.volume_scale.get_value() / 100
    
    def on_txt_search_activate(self, widget):
        if any(self.model):
            self.__focus_song(self.model[0][0])

    def on_txt_search_search_changed(self, widget):
        self.model.refilter()

    def on_player_open_stream_activate(self, event):
        d = InputBox(self, "Url")
        t = d.get_text()
        if t:
            print(t)
            self.player.seek(t)

    def on_player_preferences_activate(self, event):
        pass

    def on_player_quit_activate(self, event):
        Gtk.main_quit()
        
    def on_library_scan_activate(self, event):
        threading.Thread(target=self.player.library.sync).start() 
    
    
    def on_library_scan_finished(self):
        self.on_sort_radio_toggled(None)

    def on_library_artworks_activate(self, event):
        threading.Thread(target=lambda: self.player.library.sync_artwork(self.appconfig.LASTFM_SECRET_API_KEY)).start() 

    def on_queue_add_activate(self, event):
        self.player.queue.clear()
        self.player.queue.append([x.Path for x in self.player.library.search_song()])
        self.player.queue.seek(self.player.queue.pop())

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
    
    def on_prp_current_time_click(self, widget, event):
        width = self.prb_current_time.get_allocated_width()
        duration = self.player.streamer.duration
        self.player.streamer.position = duration * event.x / width

    def on_tick(self, data):
        position = self.player.streamer.position
        duration = self.player.streamer.duration
        fraction = position / duration if duration else 0  
        position_text = arrow.get(0).shift(seconds=position).format('mm:ss')
        duration_text = arrow.get(0).shift(seconds=duration).format('mm:ss')

        self.lbl_current_time.set_text(f'[{position_text}/{duration_text}]')
        self.prb_current_time.set_fraction(fraction)

        return True    

    def on_sort_radio_toggled(self, widget):
        if widget.get_active() or not isinstance(widget, Gtk.RadioButton):
            order = ''
            desc = self.chk_sort_desc.get_active()
            if self.radio_sort_artist.get_active():
                order = 'Artist'
            elif self.radio_sort_album.get_active():
                order = 'Album'
            elif self.radio_sort_title.get_active():
                order = 'Title'
            elif self.radio_sort_length.get_active():
                order = 'Length'
            elif self.radio_sort_year.get_active():
                order = 'Year'
            elif self.radio_sort_added.get_active():
                order = 'Added'
            elif self.radio_sort_played.get_active():
                order = 'Played'

            threading.Thread(target=lambda: self.__create_model(self.player.library.search_song(order, desc))).start()
    

    def on_leftmenu_selected_rows_changed(self, widget):
        label = widget.get_selected_row().get_children()[0]
        # if label.get_text() == "Local":
        #     threading.Thread(target=lambda:self.__create_model(self.player.library.search_song())).start()
        # elif label.get_text() == "Queue":
        #     threading.Thread(target=lambda:self.__create_model(self.player.library.get_songs([x for x in self.player.queue]))).start()
