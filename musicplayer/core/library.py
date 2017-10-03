import time
import logging
import mimetypes
import pathlib

from musicplayer.core.database import database_context, Song, Album, Artist, Playlist
from musicplayer.core.playlist_m3u import PlaylistM3u
from musicplayer.core.fetchers import artworks

class Library(object):
    """Explore the music folder and extract songs, album, artist into the database

    Attributes:
        _musics_folder: A string indicating where the musics is located
        _playlist_folder: A string indicating where the playlists is located

    """

    INGORE_EXTENSION = {'.jpg', '.jpeg', '.db',
                        '.ini', '.png', '.bmp', '.pdf',
                        '.tif', '.txt', '.nfo',}

    def __init__(self, appconfig, userconfig):
        self.logger = logging.getLogger('Library')
        database_context.init(appconfig.DATABASE_FILE)

        Song.create_table(True)
        Album.create_table(True)
        Artist.create_table(True)
        Playlist.create_table(True)

        self.appconfig = appconfig
        self.userconfig = userconfig

        self._musics_folder = self.userconfig["library"]["music_directory"]
        self._playlists_folder = self.userconfig["library"]["playlist_directory"]
        self._artworks_folder = self.appconfig.ARTWORK_CACHE_DIRECTORY

    def get_songs(self, path_list):
        return Song.select().where(Song.Path << path_list)

    def get_song(self, path):
        try:
            return Song.get(Song.Path==path)
        except:
            return None

    def get_album(self, name, albumartist):
        try:
            return Album.get(Album.Name==name, Album.Artist==albumartist)
        except:
            return None

    def search_song(self, order=None, desc=False):
        order_fields = []

        if not order or order == 'Artist':
            order_fields = [Song.AlbumArtist,
                            Song.Year,
                            Song.Album,
                            Song.Discnumber,
                            Song.Tracknumber]

        elif order == 'Album':
            order_fields = [Song.Album,
                            Song.Discnumber,
                            Song.Tracknumber]

        elif order == 'Year':
            order_fields = [Song.Year,
                            Song.Album,
                            Song.Discnumber,
                            Song.Tracknumber]

        elif order == 'Added':
            order_fields = [Song.Added,
                            Song.AlbumArtist,
                            Song.Year,
                            Song.Album,
                            Song.Discnumber,
                            Song.Tracknumber]

        elif order == 'Title':
            order_fields = [Song.Title]

        elif order == 'Length':
            order_fields = [Song.Length]

        elif order == 'Played':
            order_fields = [Song.Played]

        if desc:
            order_fields[0] = -order_fields[0]

        return Song.select().order_by(*order_fields)

    def sync_artwork(self):
        """ For every album with a missing cover try to fetch it """
        list_album = Album.select()
        with database_context.atomic():
            for index, album in enumerate(list_album):
                if not album.Cover or not pathlib.Path(album.Cover).exists():
                    path = pathlib.Path(album.Path).parent if pathlib.Path(album.Path).is_file else album.Path
                    album.Cover = artworks.get_album_artwork(self.appconfig.LASTFM_SECRET_API_KEY,
                                                             self._artworks_folder, album.Name,
                                                             album.Artist, path)
                    album.save()
                if index % 10 == 0:
                    self.logger.info(f'Artworks fetch {index}/{len(list_album)}')

        self.logger.info(f'Artworks fetch completed')

    def sync(self):
        """Synchronize data from library and actual data in the musics folder

        Raises:
            ValueError: When musics_folder is not set
        """
        if self._musics_folder is None or not pathlib.Path(self._musics_folder).is_dir():
            raise ValueError('Invalid music folder: ' + str(self._musics_folder))

        self.logger.info(f"Scanning {self._musics_folder}")
        start = time.perf_counter()
        self.__sync_songs()
        self.__sync_artists()
        self.__sync_albums()
        end = time.perf_counter()
        self.logger.info('Scan ended in {:.3f}'.format(end - start))

    def __sync_songs(self):
        paths = []
        for x in pathlib.Path(self._musics_folder).glob('**/*'):
            if x.is_dir():
                continue
            if x.suffix.lower() in self.INGORE_EXTENSION:
                continue
            paths.append(str(x.resolve(False)))

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
        if self._playlists_folder is None or not pathlib.Path(self._playlists_folder).is_dir():
            return

        list_path = set(str(x) for x in pathlib.Path(
            self._playlists_folder).glob('**/*m3u'))

        with database_context.atomic():
            for path in list_path:
                playlist = PlaylistM3u(path)
                Playlist(Name=playlist.name, Path=playlist.location).save()

    def __sync_artists(self):
        self.logger.info('Scanning artists')
        database_context.execute_sql("""
            INSERT INTO ARTIST ('Name')
            SELECT DISTINCT AlbumArtist FROM Song
            LEFT JOIN Artist ON Song.AlbumArtist = Artist.Name
            WHERE AlbumArtist != '' AND ArtistId IS NULL
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

    # def vplayer_library_converter(self):
    #     import udatetime, json, gzip, os
    #     with DB.atomic():
    #         with gzip.open('/run/media/vincent/D-DRV/Documents/Autre/Dotfiles/VPlayer/library.gz', mode="rt") as f:
    #             json_library = json.loads(f.read())
    #             songs = json_library["songs"]
    #             for index, x in enumerate(songs):
    #                 for real in Song.select().where(Song.Path ** ('%' + x['path'][-20:])):
    #                     if os.path.samefile(real.Path, x['path']):
    #                         real.Added = udatetime.from_string(x.get('added', 0))
    #                         real.save()
    #                         break
    #                 if (index % 10 == 0):
    #                     print(f'{index}/{len(songs)}')
