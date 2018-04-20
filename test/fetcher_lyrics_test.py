import unittest

from mokaplayer.core.fetchers import lyrics as lyricsfetcher

class FetcherLyricsTest(unittest.TestCase):

    def test_lyrics_fetcher(self):
        success, lyrics = lyricsfetcher.get('Thriller', 'Michael Jackson', 'Thriller')
        self.assertTrue(success)
        self.assertNotRegex(lyrics, 'Lyrics not found')

    def test_provider_musicmatch(self):
        lyrics = lyricsfetcher.ProviderMusicmatch().get_lyrics('Thriller', 'Michael Jackson', 'Thriller')
        self.assertNotEqual(lyrics, '')

    def test_provider_azlyrics(self):
        lyrics = lyricsfetcher.ProviderAzLyrics().get_lyrics('Thriller', 'Michael Jackson', 'Thriller')
        self.assertNotEqual(lyrics, '')

    def test_provider_metrolyrics(self):
        lyrics = lyricsfetcher.ProviderMetrolyrics().get_lyrics('Thriller', 'Michael Jackson', 'Thriller')
        self.assertNotEqual(lyrics, '')

    def test_provider_genius(self):
        lyrics = lyricsfetcher.ProviderGenius().get_lyrics('Thriller', 'Michael Jackson', 'Thriller')
        self.assertNotEqual(lyrics, '')

    def test_provider_darklyrics(self):
        lyrics = lyricsfetcher.ProviderDarkLyrics().get_lyrics('Enter Sandman', 'Metallica', 'Metallica (Black Album)')
        self.assertNotEqual(lyrics, '')
