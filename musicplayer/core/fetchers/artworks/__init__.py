from .provider_lastfm import ProviderLastFM
from .provider_local_filesystem import ProviderLocalFileSystem


def get_album_artwork(lastfm_apikey, artwork_folder, album_name, artist_name, album_local_path):
    result = None

    if not result and album_local_path:
        result = ProviderLocalFileSystem().get_album_artwork(album_local_path)

    if not result and album_name and artist_name and lastfm_apikey:
        result = ProviderLastFM(lastfm_apikey, artwork_folder).get_album_artwork(album_name, artist_name)

    return result


def get_artist_artwork(lastfm_apikey, artwork_folder, artist_name):
    return ProviderLastFM(lastfm_apikey, artwork_folder).get_artist_artwork(artist_name)
