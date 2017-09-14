import unittest
import pathlib
import shutil
from musicplayer.core.database import Song


class TagsTest(unittest.TestCase):

    SRC_FILE = './test/data/empty.ogg'
    DST_FILE = './test/song/song.ogg'
    FOLDER = './test/song'

    def setUp(self):
        pathlib.Path(TagsTest.FOLDER).mkdir(exist_ok=True)

    def tearDown(self):
        shutil.rmtree(TagsTest.FOLDER)

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
