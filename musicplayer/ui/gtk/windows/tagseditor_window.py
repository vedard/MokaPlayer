import ast
import logging
import arrow


from gi.repository import Gtk
from gi.repository import GObject

from musicplayer.core.database import database_context
from musicplayer.ui.gtk.helper import date_helper

class TagsEditorWindow:
    def __init__(self, songs):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('musicplayer/ui/gtk/resources/tagseditor_window.ui')
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

        self.songs = songs

        self.set_text(self.txt_Path, [s.Path for s in songs])
        self.set_text(self.txt_Bitrate, [s.Bitrate for s in songs])
        self.set_text(self.txt_Channels, [s.Channels for s in songs])
        self.set_text(self.txt_Length, [date_helper.seconds_to_string(s.Length) for s in songs])
        self.set_text(self.txt_Title, [s.Title for s in songs])
        self.set_text(self.txt_Artist, [s.Artist for s in songs])
        self.set_text(self.txt_Album, [s.Album for s in songs])
        self.set_text(self.txt_Genre, [s.Genre for s in songs])
        self.set_text(self.txt_Year, [s.Year for s in songs])
        self.set_text(self.txt_Comment, [s.Comment for s in songs])
        self.set_text(self.txt_Added, [str(s.Added) for s in songs])
        self.set_text(self.txt_ArtistAlbum, [s.AlbumArtist for s in songs])
        self.set_text(self.txt_TrackNumber, [s.Tracknumber for s in songs])

    
    def get_window(self):
        return self.window

    def set_text(self, textentry, list_value):
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
                    song.Added = arrow.get(addeds[index]).naive
                    song.save()
                    song.write_tags()

            self.window.destroy()

        except Exception as e:
            logging.exception("Could not save tags")


    def on_btnCancel_clicked(self, button):
        self.window.destroy()
