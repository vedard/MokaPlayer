import gi

gi.require_version('Keybinder', '3.0')
from gi.repository import Keybinder

class KeyboardClient:
    def __init__(self, player):
        self.player = player

        Keybinder.init()
        Keybinder.bind('XF86AudioPlay', self._on_XF86AudioPlay)
        Keybinder.bind('XF86AudioNext', self._on_XF86AudioNext)
        Keybinder.bind('XF86AudioPrev', self._on_XF86AudioPrev)

    def _on_XF86AudioNext(self, key):
        self.player.next()
    
    def _on_XF86AudioPrev(self, key):
        self.player.prev()
    
    def _on_XF86AudioPlay(self, key):
        if self.player.streamer.state == self.player.streamer.State.PAUSED:
            self.player.play()
        elif self.player.streamer.state == self.player.streamer.State.PLAYING:
            self.player.pause()