import logging


class KeyboardClient:
    """ Control the musicplayer with the keyboard using PyHook3 library
        - XF86AudioNext
        - XF86AudioPrev
        - XF86AudioPlay
    """

    def __init__(self, player):
        self.player = player
        self.logger = logging.getLogger('KeyboardClient')

        try:
            import PyHook3
            hm = PyHook3.HookManager()
            hm.KeyDown = self._on_pyhook_event
            hm.HookKeyboard()
            return
        except ImportError:
            self.logger.warning('PyHook3 is needed on Window for MediaKey binding')

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

    def _on_pyhook_event(self, event):
        if event.Key == 'Media_Next_Track':
            self._on_XF86AudioNext('XF86AudioNext')
        elif event.Key == 'Media_Prev_Track':
            self._on_XF86AudioPrev('XF86AudioPrev')
        elif event.Key == 'Media_Play_Pause':
            self._on_XF86AudioPlay('XF86AudioPlay')
        return True
