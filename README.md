# MusicPlayer

A simple music player written in python 

## Configuration

#### Create the file `musicplayer/config/secret.py` with this line:
    
    LASTFM_SECRET_API_KEY = '__'


### On Windows

#### Download the following package with [MSYS2](http://www.msys2.org/):

    pacman -S mingw-w64-i686-gtk3
    pacman -S mingw-w64-i686-python3-gobject
    pacman -S mingw-w64-i686-python3-pip
    pacman -S mingw-w64-i686-gcc
    pacman -S mingw-w64-i686-taglib
    pacman -S mingw-w64-i686-python3-lxml
    pacman -S mingw-w64-i686-swig 
    pacman -S mingw-w64-i686-gst-python
    pacman -S mingw-w64-i686-gst-plugins-base
    pacman -S mingw-w64-i686-gst-plugins-good
    pacman -S mingw-w64-i686-gst-plugins-bad
    pacman -S mingw-w64-i686-gst-plugins-ugly


#### Download the pip requirements:

    mingw32-make init

#### Download pytaglib manually (if pip not working):

    git clone https://github.com/supermihi/pytaglib
    python3 setup.py --cython
    python3 setup.py build
    pip3 install -e .

### On Arch Linux

#### Download the following package:
    pacman -S gtk3
    pacman -S python3-gobject
    pacman -S python3-pip
    pacman -S gcc
    pacman -S taglib
    pacman -S gst-python
    pacman -S gst-plugins-base
    pacman -S gst-plugins-good
    pacman -S gst-plugins-bad
    pacman -S gst-plugins-ugly

#### Download the pip requirements:
    make init
