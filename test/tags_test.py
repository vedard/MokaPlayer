import unittest
import pathlib
import shutil
import logging
from mokaplayer.core.database import Song


class TagsTest(unittest.TestCase):

    SRC_FILE = './test/data/empty.ogg'
    DST_FILE = './test/song/song.ogg'
    FOLDER = './test/song'

    def setUp(self):
        pathlib.Path(TagsTest.FOLDER).mkdir(exist_ok=True)

    def tearDown(self):
        shutil.rmtree(TagsTest.FOLDER)

    def test_read_invalid_file(self):
        with self.assertLogs(level=logging.ERROR):
            tmp = Song(Path='invalid/99999999/file')
            tmp.read_tags()

    def test_save_invalid_file(self):
        with self.assertLogs(level=logging.ERROR):
            tmp = Song(Path='invalid/99999999/file')
            tmp.write_tags()

    def test_read_tags(self):
        shutil.copy(TagsTest.SRC_FILE,  TagsTest.DST_FILE)
        song = Song(Path=TagsTest.DST_FILE)
        song.read_tags()
        self.assertEqual(song.Title, 'TestTitle')
        self.assertEqual(song.Artist, 'TestArtist')
        self.assertEqual(song.Album, 'TestAlbum')

    def test_write_tags(self):
        shutil.copy(TagsTest.SRC_FILE,  TagsTest.DST_FILE)
        song = Song(Path=TagsTest.DST_FILE)
        song.read_tags()
        song.Title = 'Title 2'
        song.Artist = 'Artist 2'
        song.Album = 'Album 2'
        song.AlbumArtist = 'AlbumArtist 2'
        song.write_tags()
        song.read_tags()
        self.assertEqual(song.Title, 'Title 2')
        self.assertEqual(song.Artist, 'Artist 2')
        self.assertEqual(song.Album, 'Album 2')
        self.assertEqual(song.AlbumArtist, 'AlbumArtist 2')
