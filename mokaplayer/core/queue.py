import collections
import random


class Queue(object):
    """ Hold an id of the song that is currently playing, and all the following one.

    Attributes:
        _container: A deque representing a list of objects in a specific order
        _current: Represent last object taken in the queue
    """

    def __init__(self):
        self._container = collections.deque()
        self._current = None

    def pop(self):
        """Remove the currently playing object"""
        tmp = self._current
        self._current = None
        return tmp

    def peek(self):
        """Get the currently playing object"""
        return self._current

    def next(self):
        """Move to the next object"""
        if any(self._container):
            if self._current == self._container[0]:
                self._container.append(self._container.popleft())
            self._current = self._container[0]
        else:
            self._current = None

    def prev(self):
        """Move to the next previous"""
        if any(self._container):
            if self._current == self._container[0]:
                self._container.appendleft(self._container.pop())
            self._current = self._container[0]
        else:
            self._current = None

    def seek(self, item):
        """Move to the item"""
        if item in self._container:
            while self._current != item:
                self.next()
        else:
            self.prepend(item)
            self.next()

    def shuffle(self):
        """Shuffle the container"""
        random.shuffle(self._container)
        try:
            self._container.remove(self._current)
            self._container.appendleft(self._current)
        except ValueError:
            pass

    def append(self, container):
        """Insert objects at the end of the container"""
        if not isinstance(container, collections.MutableSequence):
            container = [container]

        for x in container:
            try:
                self._container.remove(x)
            except ValueError:
                pass
            self._container.append(x)

        if self._current is None and any(self._container):
            self._current = self._container[0]

    def prepend(self, container):
        """Insert objects at the start of the container"""
        if not isinstance(container, collections.MutableSequence):
            container = [container]

        container.reverse()

        for x in container:
            if self._current != x:
                try:
                    self._container.remove(x)
                except ValueError:
                    pass
                self._container.appendleft(x)

        try:
            self._container.remove(self._current)
            self._container.appendleft(self._current)
        except ValueError:
            pass

        if self._current is None and any(self._container):
            self._current = self._container[0]

    def remove(self, container):
        """Remove objects from the container"""
        if not isinstance(container, collections.MutableSequence):
            container = [container]

        for x in container:
            try:
                self._container.remove(x)
            except ValueError:
                pass

    def clear(self):
        """Remove every objects from the container"""
        self._container.clear()

    def __len__(self):
        return len(self._container)

    def __iter__(self):
        return iter(self._container)
