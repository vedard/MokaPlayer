#! /bin/python3

import argparse
import logging
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from musicplayer.ui.gtk.main_window import MainWindow
from musicplayer.config import appconfig as AppConfig
from musicplayer.config.userconfig import UserConfig 

def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', help='Load the developpement configuration', required=False, action='store_true')
    return parser.parse_args()

def init_configs(args):
    appconfig = AppConfig.Developpement if args.debug else AppConfig.Production
    userconfig = UserConfig(appconfig.USER_CONFIG_FILE)

    return appconfig, userconfig

def init_logging(args, appconfig):
    logging.basicConfig(level=getattr(logging, appconfig.LOG_LEVEL))

if __name__ == '__main__':
    args = init_args()
    appconfig, userconfig = init_configs(args)
    init_logging(args, appconfig)

    window = MainWindow(appconfig, userconfig)
    window.set_icon_from_file('musicplayer/resources/icon.png')
    window.show_all()
    Gtk.main()
