import datetime
import logging

import peewee
from mokaplayer.core.database import database_context

import taglib


class Song(peewee.Model):
    songId = peewee.AutoField()
    Path = peewee.CharField(index=True)
    Title = peewee.CharField(null=True, index=True)
    Album = peewee.CharField(null=True, index=True)
    Artist = peewee.CharField(null=True, index=True)
    AlbumArtist = peewee.CharField(null=True, index=True)
    Tracknumber = peewee.IntegerField(null=True, index=True)
    Genre = peewee.CharField(null=True)
    Discnumber = peewee.IntegerField(null=True, index=True)
    Comment = peewee.CharField(null=True)
    Year = peewee.CharField(null=True, index=True)
    Label = peewee.CharField(null=True)
    Lyrics = peewee.CharField(null=True)
    Added = peewee.DateField(default=datetime.date.today, index=True)
    Last_played = peewee.DateTimeField(null=True)
    Played = peewee.IntegerField(default=0)
    Length = peewee.IntegerField(null=True)
    Channels = peewee.IntegerField(null=True)
    Bitrate = peewee.IntegerField(null=True)

    class Meta:
        database = database_context

    def __get_tag_value(self, tags, name):
        l = tags.get(name, [''])
        return l[0] if any(l) else ''

    def write_tags(self):
        """ Write tags in the file
        """
        try:
            fileref = taglib.File(self.Path)

            fileref.tags['TITLE'] = [self.Title]
            fileref.tags['ALBUM'] = [self.Album]
            fileref.tags['ARTIST'] = [self.Artist]
            fileref.tags['DISCNUMBER'] = [str(self.Discnumber)]
            fileref.tags['COMMENT'] = [self.Comment]
            fileref.tags['DATE'] = [self.Year]
            fileref.tags['LABEL'] = [self.Label]
            fileref.tags['GENRE'] = [self.Genre]
            fileref.tags['TRACKNUMBER'] = [str(self.Tracknumber)]
            fileref.tags['ALBUMARTIST'] = [self.AlbumArtist]

            fileref.save()
        except:
            logging.exception('Could not write tag to ' + self.Path)

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
