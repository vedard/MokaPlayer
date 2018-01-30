import peewee
from mokaplayer.core.database import database_context


class Artist(peewee.Model):
    ArtistId = peewee.AutoField()
    Name = peewee.CharField(index=True)
    Cover = peewee.CharField(null=True)
    Biographie = peewee.CharField(null=True)

    class Meta:
        database = database_context
