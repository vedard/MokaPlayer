import logging
import random
import re

import requests
from lxml import html


class ProviderBase(object):
    def get_lyrics(self, title, artist, album):
        try:
            url = self.get_url(title, artist, album)
            xpath = self.get_xpath(title, artist, album)
            regex = self.get_regex(title, artist, album)

            headers = {
                "User-Agent": self.get_user_agent(),
                "Accept": "*/*"
            }

            logging.info('Fetching ' + url)
            response = requests.get(url, headers=headers)

            if response.ok:

                nodes = html.fromstring(response.content).xpath(xpath)
                lyrics = self.get_node_separator().join(nodes)

                if regex:
                    match = re.search(regex, lyrics, re.IGNORECASE)
                    if match is not None:
                        lyrics = match.groups('')[0]

                lyrics = lyrics.strip()

                return lyrics

            else:
                return ''
        except:
            logging.exception('Could not fetch lyrics for ' + title)
            return ''

    def get_user_agent(self):
        return random.choice([
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; FSL 7.0.6.01001)",
            "Mozilla/5.0 (iPad; U; CPU OS 4_3_2 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8H7 Safari",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3",
            "Mozilla/5.0 (Linux; Android 4.4; Nexus 5 Build/_BuildID_) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 5.1.1; Nexus 5 Build/LMY48B; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/43.0.2357.65 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; U; Android 4.1.1; en-gb; Build/KLP) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
        ])

    def get_name(self):
        pass

    def get_url(self, title, artist, album):
        pass

    def get_xpath(self, title, artist, album):
        pass

    def get_regex(self, title, artist, album):
        pass

    def get_node_separator(self):
        pass

    def encode(self, param):
        return requests.utils.quote(param)
