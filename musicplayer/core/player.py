import pathlib

from musicplayer.core.queue import Queue
from musicplayer.core.configuration import Configuration
from musicplayer.core.library import Library
from musicplayer.core.streamer import Streamer
from musicplayer.core.configuration import Configuration


class Player(object):
    def __init__(self, audio_changed=None, notify_volume=None):
        self.configuration = Configuration()
        self.queue = Queue()
        self.streamer = Streamer(about_to_finish=self.__about_to_finish,
                                 audio_changed=audio_changed, 
                                 notify_volume=notify_volume)
                                 
        self.library = Library(self.configuration["database"]["file"],
                               self.configuration["library"]["music_directory"],
                               self.configuration["library"]["playlist_directory"],
                               pathlib.Path(self.configuration.CACHE_DIRECTORY) / 'artworks' )

    def play(self):
        if self.streamer.state == Streamer.State.PAUSED:
            self.streamer.resume()
        elif self.streamer.state == Streamer.State.STOPED and self.queue.peek():
            self.streamer.play(self.queue.peek())

    def seek(self, path):
        self.queue.seek(path)
        self.streamer.play(path)

    def stop(self):
        self.streamer.stop()
        self.queue.pop()

    def pause(self):
        self.streamer.pause()

    def toggle(self):
        if self.streamer.state == Streamer.State.PLAYING:
            self.streamer.pause()
        elif self.streamer.state == Streamer.State.PAUSED:
            self.streamer.resume()
        elif self.streamer.state == Streamer.State.STOPED and self.queue.peek():
            self.streamer.play(self.queue.peek())

    def next(self):
        if len(self.queue):
            self.queue.next()
            self.streamer.play(self.queue.peek())

    def prev(self):
        if len(self.queue):
            self.queue.prev()
            self.streamer.play(self.queue.peek())
    
    def __about_to_finish(self, data):
        self.queue.next()
        self.streamer.stream = self.queue.peek()