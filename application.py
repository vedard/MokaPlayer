#! /bin/python3
import gi
gi.require_version('Gtk', '3.0')

import argparse
import signal
import logging

from gi.repository import Gtk
from gi.repository import Gio

from musicplayer.ui.gtk.windows.main_window import MainWindow
from musicplayer.core.player import Player
from musicplayer.config import appconfig as AppConfig
from musicplayer.config.userconfig import UserConfig 


class Application():
    def __init__(self):
        self.init_args()
        self.init_configs()
        self.init_logging()
        self.init_player()
        self.init_signals()
        self.init_window()

    def init_window(self):
        self.window = MainWindow(self.appconfig, self.userconfig, self.player)
        self.window.set_icon_from_file('musicplayer/resources/icon.png')
        self.window.show_all()

    def init_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--debug', help='Load the developpement configuration', required=False, action='store_true')
        self.args = parser.parse_args()

    def init_configs(self):
        self.appconfig = AppConfig.Developpement if self.args.debug else AppConfig.Production
        self.userconfig = UserConfig(self.appconfig.USER_CONFIG_FILE)

    def init_logging(self):
        logging.basicConfig(level=getattr(logging, self.appconfig.LOG_LEVEL))

    def init_player(self):
        self.player = Player(self.appconfig, self.userconfig)
        self.player.restore()
    
    def init_signals(self):
        
        def handler(signum, frame): 
            self.player.save() 
            Gtk.main_quit()

        signal.signal(signal.SIGTERM, handler)
        signal.signal(signal.SIGHUP, handler)
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGQUIT, handler)

if __name__ == '__main__':
    app = Application()
    Gtk.main()
