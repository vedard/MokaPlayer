from musicplayer.core.player import Player
from musicplayer.core.database import Song

p = Player()

p.queue.append([x.Path for x in p.library.search_song('ayreon')])
p.play()

while True:
    pass