import enum
import logging
import pathlib

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstAudio', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GstAudio, GstVideo


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

    VISUALIZER_FLAG = (1 << 3)

    Visualizers = [
        'Goom',
        'Goom2k1',
        'Spacescope',
        'Spectrascope',
        'Synaescope',
        'Wavescope',
        # 'Monoscope',
        "Libvisual Oinksie",
        "Libvisual Lv Scope",
        "Libvisual Lv Analyzer",
        "Libvisual Jakdaw",
        "Libvisual Infinite",
        "Libvisual Corona",
        "Libvisual Bumpscope",
        "Libvisual Jess",
    ]

    def __init__(self, about_to_finish=None, audio_changed=None, notify_volume=None):
        Gst.init(None)
        self.logger = logging.getLogger('Streamer')

        self._visualizer = None
        self._state = Streamer.State.STOPED
        self._playbin = Gst.ElementFactory.make('playbin')
        self._videosink = Gst.ElementFactory.make('ximagesink')
        self._equalizer = Gst.ElementFactory.make("equalizer-10bands")
        self._scaletempo = Gst.ElementFactory.make("scaletempo")
        self._audio_filter = Gst.Bin()

        self._audio_filter.add(self._scaletempo)
        self._audio_filter.add(self._equalizer)
        self._scaletempo.link(self._equalizer)
        self._audio_filter.add_pad(Gst.GhostPad.new('sink', self._scaletempo.get_static_pad('sink')))
        self._audio_filter.add_pad(Gst.GhostPad.new('src', self._equalizer.get_static_pad('src')))

        self._playbin.props.audio_filter = self._audio_filter
        self._playbin.props.video_sink = self._videosink
        self._scaletempo.props.search = 5

        # Set  callbacks
        self.audio_changed = audio_changed

        if about_to_finish is not None:
            self._playbin.connect("about-to-finish", about_to_finish)

        if notify_volume is not None:
            self._playbin.connect('notify::volume', notify_volume)

    def play(self, stream=None):
        """Start the playback of the stream"""
        self.logger.debug('Play')
        self._playbin.set_state(Gst.State.READY)
        self.logger.debug('READY')

        if stream is not None:
            self.stream = stream

        self.resume()

    def stop(self):
        """Completly stop the playback of the stream"""
        self.logger.debug('Stop')
        self._playbin.set_state(Gst.State.NULL)
        self._state = Streamer.State.STOPED
        self.logger.debug('STOPED')

    def pause(self):
        """Temporaly stop the playback of the stream"""
        self.logger.debug('Pause')
        self._playbin.set_state(Gst.State.PAUSED)
        self._state = Streamer.State.PAUSED
        self.logger.debug('PAUSED')

    def resume(self):
        """Resume a temporaly stopped playback"""
        self.logger.debug('Resume')
        self._playbin.set_state(Gst.State.PLAYING)
        self._state = Streamer.State.PLAYING
        self.logger.debug('PLAYING')

    def draw_on(self, xid):
        self.logger.debug(f'Surface:{xid}')
        self._playbin.set_window_handle(xid)

    def get_equalizer_band(self, index):
        """
        index: between 0 and 9
        value: between -24.0 and 12.0
        """
        return self._equalizer.get_property("band" + str(index))

    def set_equalizer_band(self, index, value):
        """
        index: between 0 and 9
        value: between -24.0 and 12.0
        """
        self._equalizer.set_property("band" + str(index), value)

    @property
    def visualizer(self):
        return self._visualizer

    @visualizer.setter
    def visualizer(self, value):
        self._visualizer = value.lower().replace(' ', '_') if value else ''
        self.logger.debug(f'Visualizer:{self._visualizer}')

        need_to_change_vis_plugin = (self._playbin.props.vis_plugin.name != self._visualizer
                                     if self._playbin.props.vis_plugin else True)

        if self._visualizer:
            self._playbin.props.flags = self._playbin.props.flags | self.VISUALIZER_FLAG
        else:
            self._playbin.props.flags = self._playbin.props.flags & ~self.VISUALIZER_FLAG

        if self._visualizer and need_to_change_vis_plugin:
            self._playbin.props.vis_plugin = Gst.ElementFactory.make(self._visualizer, self._visualizer)

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
        if not value:
            self._playbin.props.uri = ''
        elif not value.startswith('file://'):
            self._playbin.props.uri = pathlib.Path(value).as_uri()
        else:
            self._playbin.props.uri = value

        self.logger.info(value)
        if self.audio_changed is not None:
            self.audio_changed()

    @volume.setter
    def volume(self, value):
        if value > 1:
            value = 1
        elif value < 0:
            value = 0

        self._playbin.set_volume(GstAudio.StreamVolumeFormat.CUBIC, value)

    @position.setter
    def position(self, value):
        self.logger.debug(f'Seeking:{value}')
        self._playbin.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, value * Gst.SECOND)

    def set_playback_speed(self, value):
        self._playbin.seek(value, Gst.Format.TIME, Gst.SeekFlags.FLUSH,
                           Gst.SeekType.SET, self.position * Gst.SECOND, Gst.SeekType.NONE, 0)
