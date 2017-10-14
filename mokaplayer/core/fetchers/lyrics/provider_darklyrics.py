from .provider_base import ProviderBase


class ProviderDarkLyrics(ProviderBase):
    def get_name(self):
        return "DarkLyrics"

    def get_url(self, title, artist, album):
        return 'http://www.darklyrics.com/lyrics/{}/{}.html'.format(self.encode(artist),
                                                                    self.encode(album))

    def get_xpath(self, title, artist, album):
        return '//div[@class="lyrics"]//text()'

    def get_regex(self, title, artist, album):
        return f'\d+\.\s{title.lower()}([\S\s]*?)(\d+\.\s|$)'

    def get_node_separator(self):
        return ''

    def encode(self, param):
        param = (
            param
            .lower()
            .replace(' ', '')
            .replace('(', '')
            .replace(')', '')
            .replace('.', '')
            .replace('[', '')
            .replace(']', '')
            .replace('/', '')
            .replace('?', '')
            .replace('!', '')
            .replace("'", '')
        )

        return super().encode(param)
