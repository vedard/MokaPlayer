import datetime
import time
import pathlib
import logging
import json
import gzip
from threading import Thread

from mokaplayer.core.queue import Queue
from mokaplayer.core.event import Event
from mokaplayer.core.library import Library
from mokaplayer.core.streamer import Streamer
from mokaplayer.core.keyboard import KeyboardClient


class Player(object):

    def __init__(self, appconfig, userconfig):
        self.logger = logging.getLogger("Player")
        self.appconfig = appconfig
        self.userconfig = userconfig
        self.state_changed = Event()
        self.audio_changed = Event()
        self.volume_changed = Event()
        self.queue = Queue()
        self.streamer = Streamer(about_to_finish=self.__about_to_finish,
                                 audio_changed=self.__audio_changed,
                                 notify_volume=self.__notify_volume)

        self.library = Library(self.appconfig, self.userconfig)
        KeyboardClient(self)

    def play(self):
        self.logger.debug("Play")
        if self.streamer.state == Streamer.State.PAUSED:
            self.streamer.resume()
            self.state_changed.fire()
        elif self.streamer.state == Streamer.State.STOPED and self.queue.peek():
            self.streamer.play(self.queue.peek())
            self.state_changed.fire()

    def seek(self, path):
        self.logger.debug("Seek " + str(path))
        self.__set_play_count()
        self.queue.seek(path)
        self.streamer.play(path)

    def stop(self):
        self.logger.debug("Stop")
        self.__set_play_count()
        self.streamer.stop()
        self.queue.pop()
        self.state_changed.fire()

    def pause(self):
        self.logger.debug("Pause")
        self.streamer.pause()
        self.state_changed.fire()

    def toggle(self):
        self.logger.debug("Toggle")
        if self.streamer.state == Streamer.State.PLAYING:
            self.streamer.pause()
            self.state_changed.fire()
        elif self.streamer.state == Streamer.State.PAUSED:
            self.streamer.resume()
            self.state_changed.fire()
        elif self.streamer.state == Streamer.State.STOPED and self.queue.peek():
            self.streamer.play(self.queue.peek())
            self.state_changed.fire()

    def next(self):
        self.logger.debug("Next")
        if len(self.queue):
            self.__set_play_count()
            self.queue.next()
            self.streamer.play(self.queue.peek())
        else:
            self.stop()

        self.state_changed.fire()

    def prev(self):
        self.logger.debug("Prev")
        if len(self.queue):
            self.__set_play_count()
            self.queue.prev()
            self.streamer.play(self.queue.peek())
        else:
            self.stop()

        self.state_changed.fire()

    def restore(self):
        try:
            self.logger.info("Restoring")
            if pathlib.Path(self.appconfig.PLAYER_CACHE_FILE).is_file():
                with gzip.open(self.appconfig.PLAYER_CACHE_FILE, 'rt') as file:
                    data = json.load(file)

                    self.streamer.volume = data['Volume']
                    self.queue.clear()
                    self.queue.append(data['Queue'])
                    self.seek(data['Current'])
                    self.pause()
                    time.sleep(0.3)
                    self.streamer.position = data['Position']
        except Exception as e:
            self.logger.exception('Could not restore player state')

    def save(self):
        try:
            self.logger.info("Saving")
            pathlib.Path(self.appconfig.PLAYER_CACHE_FILE).parent.mkdir(exist_ok=True)
            with gzip.open(self.appconfig.PLAYER_CACHE_FILE, 'wt') as file:
                json.dump({
                    "Queue": list(self.queue),
                    "Current": self.queue.peek(),
                    "Position": self.streamer.position,
                    "Volume": self.streamer.volume,
                }, file)
        except Exception as e:
            self.logger.exception('Could not save player state')

    def __about_to_finish(self, data):
        self.logger.debug("About to finish")
        self.__set_play_count()
        self.queue.next()
        self.streamer.stream = self.queue.peek()

    def __audio_changed(self):
        self.logger.debug("Audio changed")
        self.audio_changed.fire()

    def __notify_volume(self, data, data2):
        self.volume_changed.fire()

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
