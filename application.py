from musicplayer.core.configuration import Configuration
from musicplayer.core.library import Library

c = Configuration()
l = Library(c["database"]["file"], c["library"]["music_directory"])
l.sync()
