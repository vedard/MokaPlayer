import unittest
import time
import os

from mokaplayer.core.streamer import Streamer

class StreamerTest(unittest.TestCase):

    SILENCE_AUDIO_FILE = os.path.abspath('test/data/silence.mp3')

    def setUp(self):
        self.streamer = Streamer()
        self.streamer.volume = 0

    def test_play_without_stream(self):
        self.streamer.play()
        self.assertEqual(self.streamer.state, self.streamer.State.PLAYING)

    def test_play_with_stream(self):
        self.streamer.play(self.SILENCE_AUDIO_FILE)
        self.assertEqual(self.streamer.state, self.streamer.State.PLAYING)

    def test_stop(self):
        self.streamer.stop()
        self.assertEqual(self.streamer.state, self.streamer.State.STOPED)

    def test_pause(self):
        self.streamer.pause()
        self.assertEqual(self.streamer.state, self.streamer.State.PAUSED)

    def test_resume(self):
        self.streamer.resume()
        self.assertEqual(self.streamer.state, self.streamer.State.PLAYING)

    def test_stream(self):
        self.streamer.stream = self.SILENCE_AUDIO_FILE
        self.assertTrue(self.streamer.stream)

    def test_invalid_stream(self):
        self.streamer.stream = None
        self.assertFalse(self.streamer.stream)

        with self.assertRaises(ValueError):
            self.streamer.stream = 'asdfasdfasdf'

    def test_volume(self):
        self.streamer.volume = -100
        self.assertEqual(self.streamer.volume, 0)
        self.streamer.volume = 100
        self.assertEqual(self.streamer.volume, 1)
        self.streamer.volume = 0.3
        self.assertAlmostEqual(self.streamer.volume, 0.3)

    def test_duration(self):
        self.streamer.play(self.SILENCE_AUDIO_FILE)
        time.sleep(.3)
        self.assertAlmostEqual(self.streamer.duration, 15.264)

    def test_position(self):
        self.streamer.play(self.SILENCE_AUDIO_FILE)
        time.sleep(.3)
        self.assertGreater(self.streamer.position, 0.2)
        self.assertLess(self.streamer.position, 0.4)

    def test_position_jump(self):
        self.streamer.play(self.SILENCE_AUDIO_FILE)
        time.sleep(.3)
        self.streamer.position = 10
        time.sleep(.3)
        self.assertGreater(self.streamer.position, 9.5)
        self.assertLess(self.streamer.position, 10.5)

