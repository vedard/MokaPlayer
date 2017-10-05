import logging
import pathlib
import uuid

import requests


class ProviderLastFM(object):
    def __init__(self, api_key, artwork_folder):
        if artwork_folder is None:
            raise TypeError('Missing required argument: artwork_folder')
        elif api_key is None:
            raise TypeError('Missing required argument: api_key')

        self.URL = 'http://ws.audioscrobbler.com/2.0/'
        self._api_key = api_key
        self._artwork_folder = artwork_folder

    def get_name(self):
        "LastFm"

    def get_album_artwork(self, album_name, artist_name):
        try:
            response = requests.get(self.URL, params={
                'method': 'album.getinfo',
                'artist': artist_name,
                'album': album_name,
                'autocorrect': '1',
                'api_key': self._api_key,
                'format': 'json'
            })

            json = response.json()

            if 'error' in json:
                logging.error('Could not fetch artwork for ' + album_name)
            else:
                image_url = json['album']['image'][:4][-1]['#text']
                if image_url:
                    filename = str(pathlib.Path(self._artwork_folder, str(uuid.uuid4())))
                    self._save_image_from_url(image_url, filename)
                    return filename

            return None

        except Exception as e:
            logging.exception('Could not fetch artwork for ' + album_name)
            return None

    def get_artist_artwork(self, artist_name):
        try:
            response = requests.get(self.URL, params={
                'method': 'artist.getinfo',
                'artist': artist_name,
                'api_key': self._api_key,
                'autocorrect': '1',
                'format': 'json'
            })

            json = response.json()

            if 'error' in json:
                logging.error('Could not fetch artwork for ' + artist_name)
                return None
            else:
                filename = str(pathlib.Path(self._artwork_folder, str(uuid.uuid4())))
                self._save_image_from_url(json['artist']['image'][2]['#text'], filename)
                return filename

        except:
            logging.exception('Could not fetch artwork for ' + artist_name)
            return None

    def _save_image_from_url(self, url, filename):
        try:
            response = requests.get(url)
            if response.ok:
                pathlib.Path(filename).parent.mkdir(exist_ok=True)

                with open(filename, 'wb') as f:
                    f.write(response.content)
                    return True
            else:
                logging.error('Could not download image from ' + url + 'response was not OK')
                return False
        except:
            logging.error('Could not download image from ' + url)
            return False
