import logging
import os
import re
import json

import requests
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
                tabs = []
                page = html.fromstring(response.content)
                json_data = page.xpath("//script[contains(text(),'window.UGAPP.store.page')]")[0].text;
                json_data = json_data[json_data.find('{'):json_data.rfind('}') + 1]
                json_data = json.loads(json_data)

                for tab_json in json_data['data']['results']:
                    if 'type_name' in tab_json and (tab_json['type_name'] == 'Tab' or tab_json['type_name'] == 'Guitar Pro'):
                        tabs.append({
                            'name': tab_json['song_name'],
                            'url': tab_json['tab_url'],
                            'rating': tab_json['rating'],
                            'votes': tab_json['votes'],
                            'type': tab_json['type_name'],
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
                json_data = page.xpath("//script[contains(text(),'window.UGAPP.store.page')]")[0].text;
                json_data = json_data[json_data.find('{'):json_data.rfind('}') + 1]
                json_data = json.loads(json_data)
                return json_data['data']['tab_view']['wiki_tab']['content']
        except:
            logging.exception('Could not fetch ascii tabs for: ' + url)

        return ''

    @staticmethod
    def download_guitar_pro_tab(url, directory):
        """Retrieve and download the guitar pro tab (file) from a url"""
        try:
            response = requests.get(url, cookies={
                                    'back_to_classic_ug': '1'
                                    })
            if response.ok:
                page = html.fromstring(response.content)
                json_data = page.xpath("//script[contains(text(),'window.UGAPP.store.page')]")[0].text
                json_data = json_data[json_data.find('{'):json_data.rfind('}') + 1]
                json_data = json.loads(json_data)

                response = requests.get(ProviderUltimateGuitar.DOWNLOAD_URL,
                                        params={
                                            'id': json_data['data']['tab']['id'],
                                        }, headers={
                                            "Referer": url,
                                        })
                filename = re.findall('filename\s*?=\s?"(.+)"',
                                      response.headers['Content-Disposition'])[0]

                os.makedirs(directory, exist_ok=True)
                path = os.path.join(directory, filename)

                with open(path, 'wb') as f:
                    f.write(response.content)
                    return path
        except:
            logging.exception('Could not download guitar pro tabs for: ' + url)

        return None
