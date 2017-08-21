from musicplayer.core.queue import Queue
from musicplayer.core.configuration import Configuration
from musicplayer.core.library import Library
from musicplayer.core.streamer import Streamer
from musicplayer.core.configuration import Configuration


class Player(object):
    def __init__(self):
        self.configuration = Configuration()
        self.queue = Queue()
        self.streamer = Streamer(about_to_finish=self.__about_to_finish,
                                 audio_changed=self.__audio_changed, 
                                 notify_volume=self.__notify_volume)
                                 
        self.library = Library(self.configuration["database"]["file"],
                               self.configuration["library"]["music_directory"],
                               self.configuration["library"]["playlist_directory"])

    def play(self):
        if self.streamer.state == Streamer.State.PAUSED:
            self.streamer.resume()
        elif self.streamer.state == Streamer.State.STOPED:
            self.next()

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

    def next(self):
        if self.queue:
            self.queue.next()
            self.streamer.play(self.queue.peek())

    def prev(self):
        if self.queue:
            self.queue.prev()
            self.streamer.play(self.queue.peek())
    
    def __about_to_finish(self, data):
        self.queue.next()
        self.streamer.stream = self.queue.peek()

    def __audio_changed(self, data):
        pass

    def __notify_volume(self, data1, data2):
        pass
