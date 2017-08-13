import peewee
import datetime

DB = peewee.SqliteDatabase(None)

class Database(object):
    """ PeeWee wrapper to save songs, artists, albums, lyrics and etc...
    """
    @staticmethod
    def connect(database_path):
        DB.init(database_path)
        Song.create_table(True)
        Album.create_table(True)
        Artist.create_table(True)


class Song(peewee.Model):
    songId = peewee.PrimaryKeyField()
    Url = peewee.CharField(index=True)
    Title = peewee.CharField(null=True, index=True)
    Album = peewee.CharField(null=True, index=True)
    Artist = peewee.CharField(null=True, index=True)
    AlbumArtist = peewee.CharField(null=True, index=True)
    Tracknumber = peewee.CharField(null=True)
    Genre = peewee.CharField(null=True)
    Discnumber = peewee.CharField(null=True)
    Comment = peewee.CharField(null=True)
    Year = peewee.CharField(null=True)
    Label = peewee.CharField(null=True)
    Lyrics = peewee.CharField(null=True)
    Added = peewee.DateTimeField(default=datetime.datetime.now, index=True)
    Last_played = peewee.DateTimeField(null=True)
    Played = peewee.IntegerField(default=0)
    Length = peewee.IntegerField(null=True)
    Channels = peewee.IntegerField(null=True)
    Bitrate = peewee.IntegerField(null=True)

    class Meta:
        database = DB


class Album(peewee.Model):
    AlbumId= peewee.PrimaryKeyField()
    Name = peewee.CharField(index=True) 
    Year = peewee.CharField(null=True)
    Cover = peewee.CharField(null=True)
    Description = peewee.CharField(null=True)
    Artist = peewee.CharField(null=True)
    
    class Meta:
        database = DB


class Artist(peewee.Model):
    ArtistId = peewee.PrimaryKeyField()
    Name = peewee.CharField(index=True)
    Cover = peewee.CharField(null=True)
    Biographie = peewee.CharField(null=True)
    
    class Meta:
        database = DB

