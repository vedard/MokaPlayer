import logging
import mimetypes
import pathlib
import peewee
import time

from mokaplayer.core.database import (Album, Artist, Playlist, Song,
                                      database_context)
from mokaplayer.core import playlists
from mokaplayer.core.fetchers import artworks
from mokaplayer.core.m3u_parser import M3uParser


class Library(object):
    """Explore the music folder and extract songs, album, artist into the database

    Attributes:
        _musics_folder: A string indicating where the musics is located
        _playlist_folder: A string indicating where the playlists is located

    """

    INGORE_EXTENSION = {'.jpg', '.jpeg', '.db',
                        '.ini', '.png', '.bmp', '.pdf',
                        '.tif', '.txt', '.nfo', }

    def __init__(self, appconfig, userconfig):
        self.logger = logging.getLogger('Library')
        database_context.init(appconfig.DATABASE_FILE)

        Song.create_table(True)
        Album.create_table(True)
        Artist.create_table(True)
        Playlist.create_table(True)

        self.appconfig = appconfig
        self.userconfig = userconfig

    def is_musics_folder_valid(self):
        if not self.musics_folder:
            return False
        else:
            return pathlib.Path(self.musics_folder).is_dir()

    @property
    def musics_folder(self):
        return self.userconfig["library"]["music_directory"]

    @musics_folder.setter
    def musics_folder(self, value):
        self.logger.debug('Setting musics_folder: ' + value)
        self.userconfig["library"]["music_directory"] = value
        self.userconfig.save()

    @property
    def playlists_folder(self):
        folder = self.userconfig["library"]["playlist_directory"]
        if not folder or not pathlib.Path(folder).is_dir():
            folder = self.musics_folder
        return folder

    @playlists_folder.setter
    def playlists_folder(self, value):
        self.userconfig["library"]["playlist_directory"] = value
        self.userconfig.save()

    @property
    def artworks_folder(self):
        return self.appconfig.ARTWORK_CACHE_DIRECTORY

    def get_songs(self, paths):
        return Song.select().where(Song.Path << paths)

    def get_song(self, path):
        try:
            path = str(pathlib.Path(path).resolve(False))
            return Song.get(Song.Path == path)
        except:
            return None

    def get_playlist(self, name):
        try:
            x = Artist.get(Artist.Name == name)
            return playlists.ArtistPlaylist(x)
        except peewee.DoesNotExist:
            pass

        try:
            x = Album.get(Album.Name == name)
            return playlists.AlbumPlaylist(x)
        except peewee.DoesNotExist:
            pass

        return None

    def get_playlists(self):
        return [playlists.M3UPlaylist(x.Path) for x in Playlist.select(Playlist.Path)]

    def get_album(self, name, albumartist):
        try:
            return Album.get(Album.Name == name, peewee.fn.lower(Album.Artist) == albumartist.lower())
        except peewee.DoesNotExist:
            return None

    def create_playlist(self, name):
        """Create a new playlist in the right folder"""

        path = pathlib.Path(self.playlists_folder) / (name + '.m3u')
        if not path.exists():
            M3uParser(str(path)).write()
            self.__sync_playlists()

    def sync_artwork(self):
        """ For every album and artist with a missing cover try to fetch it """
        with database_context.atomic():
            for album in Album.select():
                if not album.Cover or not pathlib.Path(album.Cover).exists():
                    path = pathlib.Path(album.Path).parent if pathlib.Path(album.Path).is_file else album.Path
                    album.Cover = artworks.get_album_artwork(self.appconfig.LASTFM_SECRET_API_KEY,
                                                             self.artworks_folder, album.Name,
                                                             album.Artist, path)
                    album.save()

            for artist in Artist.select():
                if not artist.Cover or not pathlib.Path(artist.Cover).exists():
                    artist.Cover = artworks.get_artist_artwork(self.appconfig.LASTFM_SECRET_API_KEY,
                                                               self.artworks_folder, artist.Name)
                    artist.save()

        self.logger.info(f'Artworks fetch completed')

    def sync(self):
        """Synchronize data from library and actual data in the musics folder

        Raises:
            ValueError: When musics_folder is not set
        """
        if self.musics_folder is None or not pathlib.Path(self.musics_folder).is_dir():
            raise ValueError('Invalid music folder: ' + str(self.musics_folder))

        self.logger.info(f"Scanning {self.musics_folder}")
        start = time.perf_counter()
        self.__sync_songs()
        self.__sync_artists()
        self.__sync_albums()
        self.__sync_playlists()
        end = time.perf_counter()
        self.logger.info('Scan ended in {:.3f}'.format(end - start))

    def __sync_songs(self):
        paths = []
        # Create a list of every potential file in the music folder
        for x in pathlib.Path(self.musics_folder).glob('**/*'):
            try:
                if x.is_dir():
                    continue
                if x.suffix.lower() in self.INGORE_EXTENSION:
                    continue
                paths.append(str(x.resolve(False)))
            except OSError:
                self.logger.exception('Error while scanning songs')

        all_paths = set(paths)
        known_paths = {x.Path for x in Song.select(Song.Path)}
        new_paths = all_paths - known_paths
        deleted_paths = known_paths - all_paths

        with database_context.atomic():
            for index, path in enumerate(new_paths):
                mime = mimetypes.guess_type(path)
                if mime[0] and 'audio' in str(mime[0]) and 'mpegurl' not in str(mime[0]):
                    s = Song(Path=path)
                    s.read_tags()
                    s.save()
                if index % 300 == 0 and index > 0:
                    self.logger.info(f'Scanning songs {index}/{len(new_paths)}')

            for song in deleted_paths:
                Song.delete().where(Song.Path == song).execute()

        self.logger.info(f'Scanning songs completed')

    def __sync_playlists(self):
        self.logger.info('Scanning playlists')

        all_paths = set(str(x) for x in pathlib.Path(self.playlists_folder).glob('**/*m3u'))
        known_paths = {x.Path for x in Playlist.select(Playlist.Path)}
        new_paths = all_paths - known_paths
        deleted_paths = known_paths - all_paths
        with database_context.atomic():
            for path in new_paths:
                playlist = M3uParser(path)
                Playlist(Name=playlist.name, Path=playlist.location).save()
            for path in deleted_paths:
                Playlist.delete().where(Song.Path == path).execute()

    def __sync_artists(self):
        self.logger.info('Scanning artists')
        database_context.execute_sql("""
            INSERT INTO ARTIST ('Name')
            SELECT DISTINCT AlbumArtist FROM Song
            LEFT JOIN Artist ON Song.AlbumArtist = Artist.Name
            WHERE AlbumArtist != '' AND ArtistId IS NULL
        """)
        database_context.execute_sql("""
            DELETE FROM Artist
            where not exists (select songid
                              from song
                              where Song.AlbumArtist = Artist.Name)
        """)

    def __sync_albums(self):
        self.logger.info('Scanning albums')
        database_context.execute_sql("""
            INSERT INTO album ('Name', 'Year', 'Path', 'Artist')
            SELECT song.album, song.year, song.path, song.albumartist
            FROM   song
            LEFT JOIN album ON album.NAME = song.album AND album.artist LIKE song.albumartist
            WHERE  song.album != '' AND album.albumid IS NULL
            GROUP  BY song.album
        """)

        database_context.execute_sql("""
            DELETE FROM Album
            where not exists (select songid
                            from song
                            where album.NAME = song.album AND
                                    album.artist LIKE song.albumartist)
        """)
