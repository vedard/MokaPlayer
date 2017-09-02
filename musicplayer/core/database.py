import datetime
import logging
import peewee
import taglib

DB = peewee.SqliteDatabase(None)

class Song(peewee.Model):
    songId = peewee.PrimaryKeyField()
    Path = peewee.CharField(index=True)
    Title = peewee.CharField(null=True, index=True)
    Album = peewee.CharField(null=True, index=True)
    Artist = peewee.CharField(null=True, index=True)
    AlbumArtist = peewee.CharField(null=True, index=True)
    Tracknumber = peewee.IntegerField(null=True, index=True)
    Genre = peewee.CharField(null=True)
    Discnumber = peewee.IntegerField(null=True)
    Comment = peewee.CharField(null=True)
    Year = peewee.CharField(null=True, index=True)
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
    
    def __get_tag_value(self, tags, name):
        l = tags.get(name, [''])
        return l[0] if any(l) else ''

    def read_tags(self):
        """ Read tags from the file
        """
        try:
            fileref = taglib.File(self.Path)
            self.Title = self.__get_tag_value(fileref.tags, 'TITLE')
            self.Album = self.__get_tag_value(fileref.tags, 'ALBUM')
            self.Artist = self.__get_tag_value(fileref.tags, 'ARTIST')
            self.Discnumber = self.__get_tag_value(fileref.tags, 'DISCNUMBER')
            self.Comment = self.__get_tag_value(fileref.tags, 'COMMENT')
            self.Year = self.__get_tag_value(fileref.tags, 'DATE')[:4]
            self.Label = self.__get_tag_value(fileref.tags, 'LABEL')
            self.Lyrics = self.__get_tag_value(fileref.tags, 'LYRICS')
            self.Genre = self.__get_tag_value(fileref.tags, 'GENRE')
            self.Tracknumber = self.__get_tag_value(fileref.tags, 'TRACKNUMBER')
            self.AlbumArtist = self.__get_tag_value(fileref.tags, 'ALBUMARTIST') 
            self.Length = fileref.length
            self.Channels = fileref.channels
            self.Bitrate = fileref.bitrate

            try:
                self.Tracknumber = int(self.Tracknumber.split('/')[0])
            except ValueError:
                self.Tracknumber = 0

            try:
                self.Discnumber = int(self.Discnumber.split('/')[0])
            except ValueError:
                self.Discnumber = 0

            self.AlbumArtist = self.AlbumArtist or self.Artist


        except:
            logging.exception('Could not read tag from ' + self.Path)


class Album(peewee.Model):
    AlbumId= peewee.PrimaryKeyField()
    Name = peewee.CharField(index=True) 
    Path = peewee.CharField(index=True) 
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

class Playlist(peewee.Model):
    PlaylistId = peewee.PrimaryKeyField()
    Name = peewee.CharField(index=True)
    Path = peewee.CharField()

    class Meta:
        database = DB
