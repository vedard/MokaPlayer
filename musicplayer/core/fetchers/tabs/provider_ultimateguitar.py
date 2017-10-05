import requests
import os
import re
import logging
from lxml import html


class ProviderUltimateGuitar():

    SEARCH_URL = 'https://www.ultimate-guitar.com/search.php'
    DOWNLOAD_URL = 'https://tabs.ultimate-guitar.com/tab/download'

    @staticmethod
    def search(title, artist):
        """ Return a list of tabs (a dict with all infos) that can be fetched or downloaded"""

        response = requests.get(ProviderUltimateGuitar.SEARCH_URL,
                                params={
                                    'band_name': artist,
                                    'song_name': title,
                                    'type[]': ['200', '500'],  # tab and guitar pro
                                })

        if response.ok:
            try:
                page = html.fromstring(response.content)
                rows = page.xpath('//tr[.//a[contains(@class, "song") and contains(@class ,"result-link")]]')
                tabs = []

                for row in rows:
                    song = row.xpath('.//a[contains(@class, "song") and contains(@class ,"result-link")]')[0]
                    tab_type = row.xpath('./td[last()]//strong//text()')[0]
                    rating = row.xpath('.//b[contains(@class, "ratdig")]//text()')
                    rating = rating[0] if any(rating) else '0'

                    if tab_type == 'guitar pro' or tab_type == 'tab':
                        tabs.append({
                            'name': ' '.join(song.xpath('.//text()')).strip(),
                            'url': song.attrib['href'],
                            'rating': int(str(rating)),
                            'type': tab_type
                        })

                return sorted(tabs, key=lambda tab: (tab['type'],
                                                     -tab['rating']))
            except:
                logging.exception('Could not search guitar tabs for: ' + title)

        return []

    @staticmethod
    def fetch_ascii_tab(url):
        """Retrieve the ascii tab from a url"""
        try:
            response = requests.get(url)
            if response.ok:
                page = html.fromstring(response.content)
                nodes = page.xpath('//pre[contains(@class, "js-tab-content")]/text()')

                if any(nodes):
                    return nodes[0]
        except:
            logging.exception('Could not fetch ascii tabs for: ' + url)

        return ''

    @staticmethod
    def download_guitar_pro_tab(url, directory):
        """Retrieve and download the guitar pro tab (file) from a url"""
        try:
            response = requests.get(url)
            if response.ok:
                page = html.fromstring(response.content)
                nodes = page.xpath('//input[@id="tab_id"]/@value')

                if any(nodes):
                    try:
                        response = requests.get(ProviderUltimateGuitar.DOWNLOAD_URL,
                                                params={
                                                    'id': nodes[0]
                                                })
                        filename = re.findall('filename\s*?=\s?"(.+)"',
                                              response.headers['Content-Disposition'])[0]

                        os.makedirs(directory, exist_ok=True)
                        path = os.path.join(directory, filename)

                        with open(path, 'wb') as f:
                            f.write(response.content)
                            return path
                    except:
                        logging.exception('Could not download guitar pro tabs for id: ' + nodes[0])

        except:
            logging.exception('Could not download guitar pro tabs for: ' + url)

        return None
