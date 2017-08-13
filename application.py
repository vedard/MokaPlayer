from musicplayer.core.configuration import Configuration
from musicplayer.core.database import Database
from musicplayer.core.database import Artist

c = Configuration()
Database.connect(c["database"]["file"])
Artist(Name='test').save()

for a in Artist.select():
    print(a.Name)