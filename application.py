#! /bin/python3

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from musicplayer.ui.gtk.main_window import MainWindow
import datetime

if __name__ == '__main__':
    window = MainWindow()
    window.show_all()
    Gtk.main()
