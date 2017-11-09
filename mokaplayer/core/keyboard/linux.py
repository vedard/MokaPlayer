import logging


class KeyboardClient:
    """ Control the musicplayer with the keyboard using Keybinder library
        - XF86AudioNext
        - XF86AudioPrev
        - XF86AudioPlay
    """

    def __init__(self, player):
        self.player = player
        self.logger = logging.getLogger('KeyboardClient')

        try:
            import gi
            gi.require_version('Keybinder', '3.0')
            from gi.repository import Keybinder
            Keybinder.init()
            Keybinder.bind('XF86AudioPlay', self._on_XF86AudioPlay)
            Keybinder.bind('XF86AudioNext', self._on_XF86AudioNext)
            Keybinder.bind('XF86AudioPrev', self._on_XF86AudioPrev)
        except ValueError:
            self.logger.warning('Keybinder is needed on Linux for MediaKey binding')

    def _on_XF86AudioNext(self, key):
        self.logger.info(key)
        self.player.next()

    def _on_XF86AudioPrev(self, key):
        self.logger.info(key)
        self.player.prev()

    def _on_XF86AudioPlay(self, key):
        self.logger.info(key)
        if self.player.streamer.state == self.player.streamer.State.PAUSED:
            self.player.play()
        elif self.player.streamer.state == self.player.streamer.State.PLAYING:
            self.player.pause()
