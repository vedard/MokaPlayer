import logging
import pathlib


class M3uParser:
    """Represent a list of path or url (media file) loaded from a M3U file

    Properties:
        location: A string representing the location of the playlist File
        name: A string representing the name of the file
    """

    def __init__(self, location):
        if not pathlib.Path(location).parent.is_dir():
            raise ValueError('Directory does not exist for: ' + location)

        self._location = location
        self._name = ''
        self._media_files = []

    def read(self):
        try:
            logging.debug('Reading playlist from ' + self.location)
            self.clear()
            with open(self.location, 'rt') as f:
                for line in f.read().split('\n'):
                    if line and not line.startswith('#EXT'):
                        self._media_files.append(line)
        except:
            logging.exception('Could not read playlist from ' + self.location)

    def write(self):
        """Write songs to the playlist file"""
        try:
            logging.debug('Writting playlist to ' + self.location)
            with open(self.location, 'wt') as f:
                f.write('#EXTM3U\n')
                for path in self._media_files:
                    f.write(path + '\n')
        except:
            logging.exception('Could not write playlist to ' + self.location)

    def clear(self):
        self._media_files.clear()

    def __len__(self):
        return len(self._media_files)

    def __iter__(self):
        self.read()
        return iter(self._media_files)

    def __getitem__(self, key):
        return self._media_files[key]

    def __setitem__(self, key, value):
        self._media_files[key] = value

    def __delitem__(self, key):
        del(self._media_files[key])

    def append(self, value):
        for file in self._media_files:
            if pathlib.Path(file).resolve() == pathlib.Path(value).resolve():
                return

        self._media_files.append(value)

    def remove(self, value):
        for file in list(self._media_files):
            if pathlib.Path(file).resolve() == pathlib.Path(value).resolve():
                self._media_files.remove(file)
                return

    @property
    def location(self):
        return self._location

    @property
    def name(self):
        if self._name:
            return self._name
        else:
            self._name = pathlib.Path(self.location).stem
            return self._name

    @name.setter
    def name(self, value):
        try:
            path = pathlib.Path(self.location)
            new_path = path.with_name(value + '.m3u')
            path.rename(new_path)
            self._name = value
            self._location = str(new_path)
        except:
            raise ValueError('Invalid name')
