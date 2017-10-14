from .provider_ultimateguitar import ProviderUltimateGuitar


def search(title, artist):
    return ProviderUltimateGuitar.search(title, artist)


def fetch_ascii_tab(url):
    return ProviderUltimateGuitar.fetch_ascii_tab(url)


def download_guitar_pro_tab(url, directory):
    return ProviderUltimateGuitar.download_guitar_pro_tab(url, directory)
