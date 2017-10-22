import shutil
import time
import uuid
import unittest
import pathlib
from mokaplayer.core.library import Library
from mokaplayer.core.database import Song, Artist, Playlist, Album
from mokaplayer.core.m3u_parser import M3uParser
from mokaplayer.config import appconfig, userconfig


class LibraryTest(unittest.TestCase):

    FOLDER = './test/library/'
    PLAYLIST_FILE = './test/library/playlist.m3u'
    SRC_FILE = './test/data/empty.ogg'
    DST_FILE = [
        './test/library/song1.ogg',
        './test/library/song2.ogg',
        './test/library/song3.ogg',
        './test/library/song4.ogg',
        './test/library/song5.ogg',
        './test/library/song6.ogg',
        './test/library/song7.ogg',
        './test/library/song8.ogg',
    ]

    def setUp(self):
        pathlib.Path(LibraryTest.FOLDER).mkdir(exist_ok=True)

        usrcfg = userconfig.UserConfig()
        usrcfg['library'] = {}
        usrcfg['library']['music_directory'] = self.FOLDER
        usrcfg['library']['playlist_directory'] = self.FOLDER

        self.library = Library(appconfig.Testing, usrcfg)

        (pathlib.Path(self.FOLDER) / 'fake.png').touch()
        (pathlib.Path(self.FOLDER) / 'fakefolder').mkdir()

        # Create 8 songs on 4 different album from 2 different artist
        for index, path in enumerate(LibraryTest.DST_FILE):
            shutil.copy(LibraryTest.SRC_FILE,  path)
            song = Song(Path=path)
            song.read_tags()
            song.Title = 'Title' + str(index)
            song.AlbumArtist = 'Artist' + str(int(index / 4))
            song.Artist = 'Artist' + str(int(index / 4))
            song.Album = 'Album' + str(int(index / 2))
            song.write_tags()

        playlist = M3uParser(LibraryTest.PLAYLIST_FILE)
        for path in LibraryTest.DST_FILE:
            playlist.append(pathlib.Path(path).name)
        playlist.write()


    def tearDown(self):
        shutil.rmtree(LibraryTest.FOLDER)

    def test_musics_folder(self):
        self.assertTrue(self.library.is_musics_folder_valid())
        self.library.musics_folder = 'asdf/Invalid folder/fasdfasdf'
        self.assertEqual(self.library.musics_folder, 'asdf/Invalid folder/fasdfasdf')
        self.assertFalse(self.library.is_musics_folder_valid())
        self.library.musics_folder = ''
        self.assertFalse(self.library.is_musics_folder_valid())
        self.library.musics_folder = self.FOLDER
        self.assertTrue(self.library.is_musics_folder_valid())
        self.assertEqual(self.library.musics_folder, self.FOLDER)

    def test_playlists_folder(self):
        self.assertEqual(self.library.playlists_folder, self.FOLDER)
        self.library.playlists_folder = 'asdf/Invalid folder/fasdfasdf'
        self.assertEqual(self.library.playlists_folder, self.FOLDER)
        self.library.playlists_folder = './test'
        self.assertEqual(self.library.playlists_folder, './test')

    def test_sync(self):
        self.library.sync()

        time.sleep(1)
        self.assertEqual(Song.select().count(), 8)
        self.assertEqual(Artist.select().count(), 2)
        self.assertEqual(Album.select().count(), 4)
        self.assertEqual(Playlist.select().count(), 1)

        self.library.sync()

        self.assertEqual(Song.select().count(), 8)
        self.assertEqual(Artist.select().count(), 2)
        self.assertEqual(Album.select().count(), 4)
        self.assertEqual(Playlist.select().count(), 1)

    def test_sync_with_delete(self):
        self.library.sync()

        for index, path in enumerate(LibraryTest.DST_FILE):
            if index != 0:
                pathlib.Path(path).unlink()

        pathlib.Path(self.PLAYLIST_FILE).unlink()

        self.library.sync()

        self.assertEqual(Song.select().count(), 1)
        self.assertEqual(Album.select().count(), 1)
        self.assertEqual(Artist.select().count(), 1)
        self.assertEqual(Playlist.select().count(), 0)

    def test_sync_with_add(self):
        self.library.sync()

        new_song_path = './test/library/songa.ogg'
        shutil.copy(LibraryTest.SRC_FILE,  new_song_path)

        song = Song(Path=new_song_path)
        song.read_tags()
        song.Title = 'Title!'
        song.Artist = 'Artist!'
        song.Album = 'Album!'
        song.write_tags()

        self.library.sync()

        self.assertEqual(Song.select().count(), 9)
        self.assertEqual(Artist.select().count(), 3)
        self.assertEqual(Album.select().count(), 5)