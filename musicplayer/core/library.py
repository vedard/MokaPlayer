import logging
import mimetypes
import pathlib

from musicplayer.core.database import DB, Song, Album, Artist, Playlist
from musicplayer.core.playlist_m3u import PlaylistM3u
from musicplayer.core.fetchers import artworks

class Library(object):
    """Explore the music folder and extract songs, album, artist into the database

    Attributes:
        _musics_folder: A string indicating where the musics is located
        _playlist_folder: A string indicating where the playlists is located

    """

    def __init__(self, database_path, musics_folder=None, playlists_folder=None, artworks_folder=None):
        DB.init(database_path)

        Song.create_table(True)
        Album.create_table(True)
        Artist.create_table(True)
        Playlist.create_table(True)

        self._musics_folder = musics_folder
        self._playlists_folder = playlists_folder
        self._artworks_folder = artworks_folder
    
    def get_songs(self, path_list):
        return Song.select().where(Song.Path << path_list)
    
    def get_song(self, path):
        try:
            return Song.get(Song.Path==path)
        except:
            return None

    def get_album(self, name):
        try:
            return Album.get(Album.Name==name)
        except:
            return None

    def search_song(self, text=None):
        if text:
            text = f'%{text}%' 
            query = Song.select().where(Song.Title ** text
                               | Song.AlbumArtist ** text
                               | Song.Album ** text
                               | Song.Year ** text
                               | Song.Artist ** text)
        else:
            query = Song.select()

        return query.order_by(Song.AlbumArtist or Song.Artist,
                              Song.Year,
                              Song.Album,
                              Song.Discnumber,
                              Song.Tracknumber)
    
    def sync_artwork(self, lastfm_apikey):
        """ For every album with a missing cover try to fetch it """
        list_album = Album.select()
        with DB.atomic():
            for index, album in enumerate(list_album):
                if not album.Cover or not pathlib.Path(album.Cover).exists():
                    path = pathlib.Path(album.Path).parent if pathlib.Path(album.Path).is_file else album.Path
                    cover = artworks.get_album_artwork(lastfm_apikey, self._artworks_folder, album.Name, album.Artist, path)
                    album.Cover = cover
                    album.save()
                if index % 10 == 0:
                    print(f'{index}/{len(list_album)}')

    def sync(self):
        """Synchronize data from library and actual data in the musics folder

        Raises:
            ValueError: When musics_folder is not set
        """
        if self._musics_folder is None:
            raise ValueError('Invalid music folder')

        logging.debug('Library sync started')
        self.__sync_songs()
        self.__sync_artists()
        self.__sync_albums()
        logging.debug('Library sync ended')

    def __sync_songs(self):
        list_all_path = set(str(x.resolve(False)) for x in pathlib.Path(self._musics_folder).glob('**/*') if not x.is_dir())
        list_known_path = set([x.Path for x in Song.select(Song.Path)])
        list_new_path = set( [x for x in list_all_path if x not in list_known_path])
        list_deleted_song = set( [x for x in list_known_path if x not in list_all_path])

        with DB.atomic():
            for index, path in enumerate(list_new_path):
                mime = mimetypes.guess_type(path)
                if mime[0] and 'audio' in mime[0] and 'mpegurl' not in mime[0]:
                    s = Song(Path=path)
                    s.read_tags()
                    s.save()
                    if index % 10 == 0:
                        print(f'{index}/{len(list_new_path)}')

            for song in list_deleted_song:
                Song.delete().where(Song.Path == song).execute()

    def __sync_playlists(self):
        if self._playlists_folder is None or not pathlib.Path(self._playlists_folder).is_dir():
            return

        list_path = set(str(x) for x in pathlib.Path(
            self._playlists_folder).glob('**/*m3u'))

        with DB.atomic():
            for path in list_path:
                playlist = PlaylistM3u(path)
                Playlist(Name=playlist.name, Path=playlist.location).save()

    def __sync_artists(self):
        DB.execute_sql("""
            INSERT INTO ARTIST ('Name') 
            SELECT DISTINCT AlbumArtist FROM Song 
            LEFT JOIN Artist ON Song.AlbumArtist = Artist.Name
            WHERE AlbumArtist != '' AND ArtistId IS NULL
        """)

    def __sync_albums(self):
        DB.execute_sql("""
            INSERT INTO album ('Name', 'Year', 'Path', 'Artist')
            SELECT song.album, song.year, song.path, CASE WHEN song.albumartist ='' THEN song.artist ELSE song.albumartist END FROM song  
            LEFT JOIN album ON album.name=song.album
            WHERE song.album != '' and album.albumid IS NULL
            GROUP BY song.album 
        """)
