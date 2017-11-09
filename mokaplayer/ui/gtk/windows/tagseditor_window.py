import ast
import logging

import arrow
import pkg_resources
from gi.repository import GObject, Gtk
from mokaplayer.core.database import database_context
from mokaplayer.core.helpers import time_helper


class TagsEditorWindow:

    GLADE_FILE = pkg_resources.resource_filename('mokaplayer',
                                                 'data/ui/tagseditor_window.ui')

    def __init__(self, songs):
        self.songs = songs

        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.GLADE_FILE)
        self.builder.connect_signals(self)

        self.window = self.builder.get_object("tagseditor_window")
        self.txt_Title = self.builder.get_object("txt_Title")
        self.txt_Artist = self.builder.get_object("txt_Artist")
        self.txt_ArtistAlbum = self.builder.get_object("txt_ArtistAlbum")
        self.txt_Album = self.builder.get_object("txt_Album")
        self.txt_TrackNumber = self.builder.get_object("txt_TrackNumber")
        self.txt_Year = self.builder.get_object("txt_Year")
        self.txt_Genre = self.builder.get_object("txt_Genre")
        self.txt_Added = self.builder.get_object("txt_Added")
        self.txt_Comment = self.builder.get_object("txt_Comment")
        self.txt_Length = self.builder.get_object("txt_Length")
        self.txt_Channels = self.builder.get_object("txt_Channels")
        self.txt_Bitrate = self.builder.get_object("txt_Bitrate")
        self.txt_Path = self.builder.get_object("txt_Path")

        self.load_text()

    def load_text(self):
        self.set_text(self.txt_Path, lambda s: s.Path)
        self.set_text(self.txt_Bitrate, lambda s: s.Bitrate)
        self.set_text(self.txt_Channels, lambda s: s.Channels)
        self.set_text(self.txt_Length,
                      lambda s: time_helper.seconds_to_string(s.Length))
        self.set_text(self.txt_Title, lambda s: s.Title)
        self.set_text(self.txt_Artist, lambda s: s.Artist)
        self.set_text(self.txt_Album, lambda s: s.Album)
        self.set_text(self.txt_Genre, lambda s: s.Genre)
        self.set_text(self.txt_Year, lambda s: s.Year)
        self.set_text(self.txt_Comment, lambda s: s.Comment)
        self.set_text(self.txt_Added, lambda s: str(s.Added))
        self.set_text(self.txt_ArtistAlbum, lambda s: s.AlbumArtist)
        self.set_text(self.txt_TrackNumber, lambda s: s.Tracknumber)

    def get_window(self):
        return self.window

    def set_text(self, textentry, field):
        list_value = [field(s) for s in self.songs]
        # If every item are the same http://stackoverflow.com/a/3844948
        if list_value.count(list_value[0]) == len(list_value):
            textentry.set_text(str(list_value[0]))
        else:
            textentry.set_text(str(list_value))

    def get_value(self, textentry):
        text = textentry.get_text()

        if text.lstrip().startswith('[') and text.rstrip().endswith(']'):
            return ast.literal_eval(textentry.get_text())
        else:
            return [text for x in range(len(self.songs))]

    def on_btnSave_clicked(self, button):
        try:
            titles = self.get_value(self.txt_Title)
            artists = self.get_value(self.txt_Artist)
            artistalbums = self.get_value(self.txt_ArtistAlbum)
            albums = self.get_value(self.txt_Album)
            tracknumbers = self.get_value(self.txt_TrackNumber)
            years = self.get_value(self.txt_Year)
            addeds = self.get_value(self.txt_Added)
            genres = self.get_value(self.txt_Genre)
            comments = self.get_value(self.txt_Comment)

            with database_context.atomic():
                for index, song in enumerate(self.songs):
                    song.Title = titles[index]
                    song.Artist = artists[index]
                    song.AlbumArtist = artistalbums[index]
                    song.Album = albums[index]
                    song.Tracknumber = tracknumbers[index]
                    song.Year = years[index]
                    song.Comment = comments[index]
                    song.Genre = genres[index]
                    song.Added = arrow.get(addeds[index]).naive.date()
                    song.save()
                    song.write_tags()

            self.window.destroy()

        except Exception as e:
            logging.exception("Could not save tags")

    def on_btnCancel_clicked(self, button):
        self.window.destroy()
