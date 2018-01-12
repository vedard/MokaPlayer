import datetime
import gzip
import json
import logging
import pathlib
import time
from threading import Thread

from mokaplayer.core.helpers.event import Event
from mokaplayer.core.keyboard import KeyboardClient
from mokaplayer.core.library import Library
from mokaplayer.core.queue import Queue
from mokaplayer.core.streamer import Streamer


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
        self.queue.pop()
        self.streamer.stop()
        self.state_changed.fire()
        self.audio_changed.fire()

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
                    self.streamer.volume = data.get('Volume', 50)
                    self.queue.clear()
                    if self.userconfig['player']['restore_queue']:
                        self.queue.append(data.get('Queue', []))
                        self.seek(data['Current'])
                        self.pause()
                        time.sleep(0.3)
                        if self.userconfig['player']['restore_song_progress']:
                            self.streamer.position = data.get('Position', 0)

                    for i, x in enumerate(data.get('Equalizer', [])):
                        self.streamer.set_equalizer_band(i, x)

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
                    "Equalizer": [self.streamer.get_equalizer_band(x) for x in range(10)]
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
