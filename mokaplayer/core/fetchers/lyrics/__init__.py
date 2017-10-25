import random
import requests

from .provider_azlyrics import ProviderAzLyrics
from .provider_darklyrics import ProviderDarkLyrics
from .provider_genius import ProviderGenius
from .provider_metrolyrics import ProviderMetrolyrics
from .provider_musixmatch import ProviderMusicmatch


def get(title, artist, album=''):
    providers = [
        ProviderAzLyrics(),
        ProviderDarkLyrics(),
        ProviderGenius(),
        ProviderMetrolyrics(),
        ProviderMusicmatch(),
    ]
    random.shuffle(providers)

    for provider in providers:
        lyrics = provider.get_lyrics(title, artist, album)

        if lyrics:
            return True, lyrics + "\n\nfrom " + provider.get_name()

    return False, ("Lyrics not found, try this: " +
                   "https://google.ca/search?q=" +
                   requests.utils.quote(f'{artist} {title} lyrics'))
