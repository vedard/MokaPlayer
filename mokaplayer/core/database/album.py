import peewee
from mokaplayer.core.database import database_context


class Album(peewee.Model):
    AlbumId = peewee.AutoField()
    Name = peewee.CharField(index=True)
    Path = peewee.CharField(index=True)
    Year = peewee.CharField(null=True)
    Cover = peewee.CharField(null=True)
    Description = peewee.CharField(null=True)
    Artist = peewee.CharField(null=True)

    class Meta:
        database = database_context
