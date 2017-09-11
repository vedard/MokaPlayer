import datetime
import time
import pathlib
import logging
import json
import gzip
from threading import Thread

from musicplayer.core.queue import Queue
from musicplayer.core.event import Event
from musicplayer.core.configuration import Configuration
from musicplayer.core.library import Library
from musicplayer.core.streamer import Streamer
from musicplayer.core.keyboard import KeyboardClient


class Player(object):

    def __init__(self, audio_changed=None, notify_volume=None, state_changed=None):
        self.state_change = Event()
        self.state_change.subscribe(state_changed)
        self.configuration = Configuration()
        self.queue = Queue()
        self.streamer = Streamer(about_to_finish=self.__about_to_finish,
                                 audio_changed=audio_changed,
                                 notify_volume=notify_volume)
                                 
        self.library = Library(self.configuration["database"]["file"],
                               self.configuration["library"]["music_directory"],
                               self.configuration["library"]["playlist_directory"],
                               pathlib.Path(self.configuration.CACHE_DIRECTORY) / 'artworks' )
        KeyboardClient(self)

    def play(self):
        if self.streamer.state == Streamer.State.PAUSED:
            self.streamer.resume()
            self.state_change.fire()
        elif self.streamer.state == Streamer.State.STOPED and self.queue.peek():
            self.streamer.play(self.queue.peek())
            self.state_change.fire()

    def seek(self, path):
        self.__set_play_count()
        self.queue.seek(path)
        self.streamer.play(path)

    def stop(self):
        self.__set_play_count()
        self.streamer.stop()
        self.queue.pop()
        self.state_change.fire()

    def pause(self):
        self.streamer.pause()
        self.state_change.fire()

    def toggle(self):
        if self.streamer.state == Streamer.State.PLAYING:
            self.streamer.pause()
            self.state_change.fire()
        elif self.streamer.state == Streamer.State.PAUSED:
            self.streamer.resume()
            self.state_change.fire()
        elif self.streamer.state == Streamer.State.STOPED and self.queue.peek():
            self.streamer.play(self.queue.peek())
            self.state_change.fire()

    def next(self):
        if len(self.queue):
            self.__set_play_count()
            self.queue.next()
            self.streamer.play(self.queue.peek())
        else:
            self.stop()

        self.state_change.fire()

    def prev(self):
        if len(self.queue):
            self.__set_play_count()
            self.queue.prev()
            self.streamer.play(self.queue.peek())
        else:
            self.stop()
    
        self.state_change.fire()

    def restore(self):
        try:
            if (pathlib.Path(self.configuration.CACHE_DIRECTORY) / 'state.gz').is_file():
                with gzip.open(pathlib.Path(self.configuration.CACHE_DIRECTORY) / 'state.gz', 'rt') as file:
                    data = json.load(file)

                    self.streamer.volume = data['Volume']
                    self.queue.clear()
                    self.queue.append(data['Queue'])
                    self.seek(data['Current'])
                    self.pause()
                    time.sleep(0.3)
                    self.streamer.position = data['Position']
        except:
            logging.error('Could not restore player state')

    def save(self):
        try:
            with gzip.open(pathlib.Path(self.configuration.CACHE_DIRECTORY) / 'state.gz', 'wt') as file:
                json.dump({
                    "Queue": list(self.queue),
                    "Current": self.queue.peek(),
                    "Position": self.streamer.position,
                    "Volume": self.streamer.volume,
                }, file)
        except:
            logging.error('Could not save player state')

    def __about_to_finish(self, data):
        self.__set_play_count()
        self.queue.next()
        self.streamer.stream = self.queue.peek()
    
    def __set_play_count(self):
        song = self.library.get_song(self.queue.peek())
        try:
            percent = self.streamer.position / self.streamer.duration
        except ZeroDivisionError:
            percent = 0
        
        if song is not None and percent > 0.85:
            song.Played += 1
            song.Last_played = datetime.datetime.now()
            Thread(target=song.save).start()
