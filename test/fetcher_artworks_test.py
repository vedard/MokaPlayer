import shutil
import unittest
import pathlib

from musicplayer.core.fetchers import artworks as artworksfetcher

class FetcherArtworkTest(unittest.TestCase):

    FOLDER = './test/artworks'

    def setUp(self):
        pathlib.Path(FetcherArtworkTest.FOLDER).mkdir(exist_ok=True)
        (pathlib.Path(FetcherArtworkTest.FOLDER) / 'test.png').touch()

    def tearDown(self):
        shutil.rmtree(FetcherArtworkTest.FOLDER)

    def test_artwork_fetcher(self):
        artist_artwork = artworksfetcher.get_artist_artwork(
            '',
            FetcherArtworkTest.FOLDER,
            'Michael Jackson'
        )
        album_artwork = artworksfetcher.get_album_artwork(
            '',
            FetcherArtworkTest.FOLDER,
            'Thriller',
            'Michael Jackson',
            None
        )

        self.assertTrue(pathlib.Path(artist_artwork).exists())
        self.assertTrue(pathlib.Path(album_artwork).exists())
        

    def test_lastfm_provider(self):
        provider = artworksfetcher.ProviderLastFM(api_key='',
                                                  artwork_folder=FetcherArtworkTest.FOLDER)

        artist_artwork = provider.get_artist_artwork('Michael Jackson')
        album_artwork = provider.get_album_artwork('Thriller',
                                                   'Michael Jackson')

        self.assertTrue(pathlib.Path(artist_artwork).exists())
        self.assertTrue(pathlib.Path(album_artwork).exists())

    def test_local_filesystem_provider(self):
        provider = artworksfetcher.ProviderLocalFileSystem()
        album_artwork = provider.get_album_artwork(FetcherArtworkTest.FOLDER)
        self.assertTrue(pathlib.Path(album_artwork).exists())
