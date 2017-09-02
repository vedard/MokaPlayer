from gi.repository import Gtk
from gi.repository import GObject
from musicplayer.core.player import Player
from musicplayer.core.configuration import Configuration
from musicplayer.ui.gtk.adapter_song import AdapterSong
from musicplayer.ui.gtk.about_window import AboutWindow
from musicplayer.ui.gtk import image_helper
import threading
import time
import datetime
import arrow

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Music Player", default_width=1366, default_height=768)
        
        self.configuration = Configuration()
        
        self.connect("destroy", self.on_window_destroy)
        
        self.builder = Gtk.Builder()
        self.builder.add_from_file('musicplayer/ui/gtk/resources/main_window.ui')
        self.builder.connect_signals(self)
        
        self.__get_object()

        self.player = Player(self.on_audio_changed, self.on_volume_changed)
        self.player.restore()

        threading.Thread(target=lambda:self.player.restore()).start()
        threading.Thread(target=lambda:self.__create_model(self.player.library.search_song())).start()

        self.gridview.set_model(AdapterSong.create_store())
        self.__set_current_song_info()

        GObject.timeout_add(500, self.on_tick, None)
 
    def __create_model(self, data):
        model = AdapterSong.create_store()
        for x in data:
            model.append(AdapterSong.create_row(x))
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
        self.add(self.content)
    
    def __set_current_song_info(self):
        song = self.player.library.get_song(self.player.queue.peek())
        album = None

        if song:
            album = self.player.library.get_album(song.Album)
            self.lbl_current_song_infos.set_text(f'{song.Artist} - {song.Album} ({song.Year})')
            self.lbl_current_title.set_text(song.Title)
        else:
            self.lbl_current_title.set_text('')
            self.lbl_current_song_infos.set_text('')

        if album:
            self.img_current_album.set_from_pixbuf(image_helper.load(album.Cover, 100, 100))
        else:
            self.img_current_album.set_from_pixbuf(image_helper.load(None, 100, 100))
    
    def __set_current_play_icon(self):
        if self.player.streamer.state == self.player.streamer.State.PLAYING:
            self.btn_play.set_image(self.img_pause)
        else:
            self.btn_play.set_image(self.img_play)
    
    def __model_filter_func(self, model, iter, data):
        return AdapterSong.search(self.txt_search.get_text(), model[iter])
    
    def on_window_destroy(self, widget):
        self.player.save()
        Gtk.main_quit()
    
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

    def on_volume_changed(self, data1, data2):
        self.volume_scale.set_value(self.player.streamer.volume * 100)
    
    def on_volume_scale_value_changed(self, widget):
        self.player.streamer.volume = self.volume_scale.get_value() / 100
    
    def on_txt_search_search_changed(self, widget):
        self.model.refilter()

    def on_player_open_stream_activate(self, event):
        pass

    def on_player_preferences_activate(self, event):
        pass

    def on_player_quit_activate(self, event):
        Gtk.main_quit()

    def on_library_scan_activate(self, event):
        threading.Thread(target=self.player.library.sync).start() 

    def on_library_artworks_activate(self, event):
        threading.Thread(target=lambda: self.player.library.sync_artwork(self.configuration['lastfm']['api_key'])).start() 

    def on_queue_add_activate(self, event):
        self.player.queue.clear()
        self.player.queue.append([x.Path for x in self.player.library.search_song()])
        self.player.queue.seek(self.player.queue.pop())

    def on_queue_clear_activate(self, event):
        self.player.queue.clear()

    def on_queue_shuffle_activate(self, event):
        self.player.queue.shuffle()

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

        self.lbl_current_time.set_text(f'{position_text} / {duration_text}')
        self.prb_current_time.set_fraction(fraction)

        return True    

    def on_leftmenu_selected_rows_changed(self, widget):
        label = widget.get_selected_row().get_children()[0]
        # if label.get_text() == "Local":
        #     threading.Thread(target=lambda:self.__create_model(self.player.library.search_song())).start()
        # elif label.get_text() == "Queue":
        #     threading.Thread(target=lambda:self.__create_model(self.player.library.get_songs([x for x in self.player.queue]))).start()