from collections import defaultdict


class Event(object):
    def __init__(self, parent, data):
        self.parent = parent
        self.data = data

    def __getattr__(self, name):
        if hasattr(self.data, name):
            return getattr(self.data, name)
        raise AttributeError


class EmitterSubscription(object):
    def __init__(self, events, func):
        self.events = events
        self.func = func

    def add(self, emitter):
        for event in self.events:
            emitter._event_handlers[event].append(self)
        return self

    def remove(self, emitter):
        for event in self.events:
            emitter._event_handlers[event].remove(self)


class Emitter(object):
    def __init__(self, wrapper=None):
        self.wrapper = wrapper
        self._event_handlers = defaultdict(list)

    def emit(self, name, *args, **kwargs):
        if name in self._event_handlers:
            for listener in self._event_handlers[name]:
                if self.wrapper:
                    self.wrapper(listener.func, *args, **kwargs)
                else:
                    listener.func(*args, **kwargs)

    def on(self, *args):
        return EmitterSubscription(args[:-1], args[-1]).add(self)
