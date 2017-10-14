import gi
gi.require_version('Gtk', '3.0')

import pkg_resources
import argparse
import signal
import logging
import threading

from gi.repository import Gtk
from gi.repository import Gio

from mokaplayer.ui.gtk.windows.main_window import MainWindow
from mokaplayer.core.player import Player
from mokaplayer.config import appconfig as AppConfig
from mokaplayer.config.userconfig import UserConfig


class Application():
    def __init__(self):
        self.init_args()
        self.init_configs()
        self.init_logging()
        self.init_player()
        self.init_signals()
        self.init_window()

    def run(self):
        Gtk.main()

    def init_window(self):
        self.window = MainWindow(self.appconfig, self.userconfig, self.player)
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
        logging.getLogger("peewee").setLevel(logging.INFO)

    def init_player(self):
        self.player = Player(self.appconfig, self.userconfig)
        threading.Thread(target=self.player.restore).start()

    def init_signals(self):

        def handler(signum, frame):
            self.player.save()
            Gtk.main_quit()

        # Some singal are not availble on every OS
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, handler)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, handler)
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, handler)
        if hasattr(signal, 'SIGQUIT'):
            signal.signal(signal.SIGQUIT, handler)