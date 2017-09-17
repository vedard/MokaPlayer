#! /bin/python3

import argparse
import logging
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from musicplayer.ui.gtk.main_window import MainWindow
from musicplayer.config import appconfig as AppConfig
from musicplayer.config.userconfig import UserConfig 

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', help='Load the developpement configuration', required=False, action='store_true')
    args = parser.parse_args()

    appconfig = AppConfig.Production
    if args.debug:
        logging.info('Loading developpement configuration')
        appconfig = AppConfig.Developpement
    
    userconfig = UserConfig(appconfig.USER_CONFIG_FILE)

    window = MainWindow(appconfig, userconfig)
    window.set_icon_from_file('musicplayer/resources/icon.png')
    window.show_all()
    Gtk.main()
