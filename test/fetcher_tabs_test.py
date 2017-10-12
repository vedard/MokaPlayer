import shutil
import unittest
import pathlib

from musicplayer.core.fetchers import tabs as tabsfetcher

@unittest.skip('')
class FetcherTabsTest(unittest.TestCase):

    FOLDER = './test/tabs'

    def setUp(self):
        pathlib.Path(FetcherTabsTest.FOLDER).mkdir(exist_ok=True)

    def tearDown(self):
        shutil.rmtree(FetcherTabsTest.FOLDER)

    def test_flow(self):
        tabs = tabsfetcher.search('Enter Sandman', 'Metallica')
        self.assertGreater(len(tabs), 0)
        self.assertIsNotNone(tabs[0])

        guitar_pro = [x for x in tabs if x['type'] == 'guitar pro'].pop()
        ascii_tab = [x for x in tabs if x['type'] == 'tab'].pop()

        ascii_text = tabsfetcher.fetch_ascii_tab(ascii_tab['url'])
        path = tabsfetcher.download_guitar_pro_tab(guitar_pro['url'], FetcherTabsTest.FOLDER)

        self.assertIsNotNone(ascii_tab)
        self.assertTrue(pathlib.Path(path).is_file())