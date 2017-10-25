import os
import subprocess
import sys


def open_file(path):
    """
    Open given file
    """
    if sys.platform.startswith('linux'):
        ret_code = subprocess.call(['xdg-open', path])

    elif sys.platform.startswith('darwin'):
        ret_code = subprocess.call(['open', path])

    elif sys.platform.startswith('win'):
        ret_code = subprocess.call(['explorer', path])

    return ret_code


def open_folder(path):
    """
    Open given folder
    """

    if os.path.isfile(path):
        path = os.path.dirname(path)

    return open_file(path)
