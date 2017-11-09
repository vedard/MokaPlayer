class Event:
    def __init__(self):
        self.__handlers = []

    def subscribe(self, handler):
        self.__handlers.append(handler)

    def unsubscribe(self, handler):
        self.__handlers.remove(handler)

    def fire(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)

    def clear(self):
        self.__handlers.clear()
