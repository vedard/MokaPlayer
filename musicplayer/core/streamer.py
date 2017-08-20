import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstAudio', '1.0')

from gi.repository import Gst, GstAudio
import pathlib
import enum

class Streamer(object):
    """ Audio engine, for playing music

    Attributes:
        _state: An enum {PLAYING, STOPED, PAUSED}
        _playbin: The gst element that can play a stream
    
    Properties:
        stream: The file or url that will play next
        state: An enum {PLAYING, STOPED, PAUSED}
        duration: A float representing the total duration of stream in seconds
        position: A float representing the position in seconds
        volume: A float (0.0 to 1.0) for the volume
    """

    class State(enum.Enum):
        PLAYING = enum.auto()
        STOPED = enum.auto()
        PAUSED = enum.auto()

    def __init__(self, about_to_finish=None, audio_changed=None, notify_volume=None):
        Gst.init(None)
        self._state = Streamer.State.STOPED
        self._playbin = Gst.ElementFactory.make('playbin', None)
        
        if about_to_finish is not None:
            self._playbin.connect("about-to-finish", about_to_finish)

        if audio_changed is not None:
            self._playbin.connect("audio-changed", audio_changed)

        if notify_volume is not None:
            self._playbin.connect('notify::volume', notify_volume)

    def play(self, stream=None):
        """Start the playback of the stream"""
        self._playbin.set_state(Gst.State.READY)
        
        if stream is not None:
            self.stream = stream

        self.resume()

    def stop(self):
        """Completly stop the playback of the stream"""
        self._playbin.set_state(Gst.State.NULL)
        self._state = Streamer.State.STOPED

    def pause(self):
        """Temporaly stop the playback of the stream"""
        self._playbin.set_state(Gst.State.PAUSED)
        self._state = Streamer.State.PAUSED

    def resume(self):
        """Resume a temporaly stopped playback"""
        self._playbin.set_state(Gst.State.PLAYING)
        self._state = Streamer.State.PLAYING
    
    @property
    def stream(self):
        return self._playbin.props.uri

    @property
    def state(self):
        return self._state

    @property
    def duration(self):
        return self._playbin.query_duration(Gst.Format.TIME)[1] / Gst.SECOND

    @property
    def position(self):
        return self._playbin.query_position(Gst.Format.TIME)[1] / Gst.SECOND

    @property
    def volume(self):
        return self._playbin.get_volume(GstAudio.StreamVolumeFormat.CUBIC)

    @stream.setter
    def stream(self, value):
        if not value.startswith('file://'):
            self._playbin.props.uri = pathlib.Path(value).as_uri()
        else:
            self._playbin.props.uri = value

    @volume.setter
    def volume(self, value):
        self._playbin.set_volume(GstAudio.StreamVolumeFormat.CUBIC, value)

    @position.setter
    def position(self, value):
        self._playbin.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, value * Gst.SECOND)
