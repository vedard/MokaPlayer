from .provider_base import ProviderBase


class ProviderMetrolyrics(ProviderBase):
    def get_name(self):
        return "metrolyrics"

    def get_url(self, title, artist, album):
        return 'http://www.metrolyrics.com/{}-lyrics-{}.html'.format(self.encode(title),
                                                                     self.encode(artist))

    def get_xpath(self, title, artist, album):
        return '//div[contains(@class, "js-lyric-text")]/p//text()'

    def get_regex(self, title, artist, album):
        return ''

    def get_node_separator(self):
        return ''

    def encode(self, param):
        param = (
            param
            .lower()
            .replace(' ', '-')
            .replace('(', '')
            .replace(')', '')
            .replace('.', '')
            .replace('/', '')
            .replace("'", '')
            .replace(',', '')
        )

        return super().encode(param)
