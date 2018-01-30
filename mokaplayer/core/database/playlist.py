import peewee
from mokaplayer.core.database import database_context


class Playlist(peewee.Model):
    PlaylistId = peewee.AutoField()
    Name = peewee.CharField(index=True)
    Path = peewee.CharField()

    class Meta:
        database = database_context
