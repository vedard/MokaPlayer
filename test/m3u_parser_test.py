import unittest
import pathlib
import shutil

from mokaplayer.core.m3u_parser import M3uParser

class M3uPaserTest(unittest.TestCase):
    FOLDER = './test/playlist/'

    def setUp(self):
        pathlib.Path(M3uPaserTest.FOLDER).mkdir(exist_ok=True)
        self.playlist = M3uParser(M3uPaserTest.FOLDER + 'test.m3u')

    def tearDown(self):
        shutil.rmtree(M3uPaserTest.FOLDER)

    def test_append_same_file(self):
        self.playlist.append('song1.mp3')
        self.playlist.append('song1.mp3')
        self.playlist.append('./song1.mp3')
        self.playlist.append('./././song1.mp3')
        self.assertEqual(len(self.playlist), 1)

    def test_readandwrite(self):
        with self.assertLogs():
            self.playlist.read()

        self.assertEqual(len(self.playlist), 0)

        self.playlist.append("song1.mp3")
        self.playlist.append("song2.wav")
        self.playlist.append("song3.ogg")
        self.playlist.append("song4.mp4")

        self.playlist.write()
        self.playlist.read()

        self.assertEqual(len(self.playlist), 4)

        self.playlist.remove("song1.mp3")
        self.assertEqual(len(self.playlist), 3)
        self.playlist.write()
        self.playlist.read()
        self.assertEqual(len(self.playlist), 3)

    def test_nameandlocation(self):
        self.assertFalse(pathlib.Path(self.playlist.location).is_file())

        self.playlist.write()

        old_location = self.playlist.location
        self.assertTrue(pathlib.Path(old_location).is_file())
        self.assertEqual(self.playlist.name, 'test')

        self.playlist.name = 'New Name'

        self.assertEqual(self.playlist.name, 'New Name')
        self.assertIn('New Name.m3u', self.playlist.location)
        self.assertTrue(pathlib.Path(self.playlist.location).is_file())
        self.assertFalse(pathlib.Path(old_location).is_file())
