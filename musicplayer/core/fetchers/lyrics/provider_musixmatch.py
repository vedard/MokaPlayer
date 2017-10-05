from .provider_base import ProviderBase


class ProviderMusicmatch(ProviderBase):
    def get_name(self):
        return "Musixmatch"

    def get_url(self, title, artist, album):
        return 'https://www.musixmatch.com/lyrics/{}/{}'.format(self.encode(artist),
                                                                self.encode(title))

    def get_xpath(self, title, artist, album):
        return '//p[@class="mxm-lyrics__content "]/text()'

    def get_regex(self, title, artist, album):
        return ''

    def get_node_separator(self):
        return '\n'

    def encode(self, param):
        param = (
            param
            .replace(' & ', '-')
            .replace('... ', '')
            .replace(' ', '-')
            .replace("'", '-')
            .replace('.', '')
            .replace('"', '')
            .replace(',', '')
            .replace('(', '')
            .replace('/', '-')
            .replace(')', '')
        )

        return super().encode(param)
