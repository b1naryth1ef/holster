from collections import defaultdict

from .enum import Enum

Priority = Enum(
        'BEFORE',
        'NONE',
        'AFTER',
)


class Event(object):
    def __init__(self, parent, data):
        self.parent = parent
        self.data = data

    def __getattr__(self, name):
        if hasattr(self.data, name):
            return getattr(self.data, name)
        raise AttributeError


class EmitterSubscription(object):
    def __init__(self, events, prio, func):
        self.events = events
        self.prio = prio
        self.func = func
        self.emitter = None

    def add(self, emitter):
        self.emitter = emitter
        for event in self.events:
            emitter.event_handlers[self.prio][event].append(self)
        return self

    def remove(self, emitter=None):
        emitter = emitter or self.emitter

        for event in self.events:
            emitter.event_handlers[self.prio][event].remove(self)


class Emitter(object):
    def __init__(self, wrapper=None):
        self.wrapper = wrapper
        self.event_handlers = {
            k: defaultdict(list) for k in Priority.attrs.values()
        }

    def _call(self, func, args, kwargs):
        if self.wrapper:
            self.wrapper(func, *args, **kwargs)
        else:
            func(*args, **kwargs)

    def emit(self, name, *args, **kwargs):
        for prio in [Priority.BEFORE, Priority.NONE, Priority.AFTER]:
            for listener in self.event_handlers[prio].get(name, []):
                self._call(listener.func, args, kwargs)

    def on(self, *args, **kwargs):
        return EmitterSubscription(args[:-1], kwargs.pop('priority', Priority.NONE), args[-1]).add(self)

    def wait(self, *args, **kwargs):
        from gevent.event import AsyncResult

        result = AsyncResult()
        match = args[-1]

        def _f(e):
            if match(e):
                result.set(e)

        return result.wait(kwargs.pop('timeout', None))
