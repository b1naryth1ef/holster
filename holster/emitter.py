from collections import defaultdict

from .enum import Enum

Priority = Enum(
        'BEFORE',
        'NONE',
        'AFTER',
)


class Stop(Exception):
    pass


class Event(object):
    def __init__(self, parent, data):
        self.parent = parent
        self.data = data

    def __getattr__(self, name):
        if hasattr(self.data, name):
            return getattr(self.data, name)
        raise AttributeError


class EmitterSubscription(object):
    def __init__(self, events, func, priority=Priority.NONE, conditional=None):
        self.events = events
        self.func = func
        self.priority = priority
        self.conditional = conditional
        self.emitter = None

    def __call__(self, *args, **kwargs):
        if callable(self.conditional):
            if not self.conditional(*args, **kwargs):
                return
        return self.func(*args, **kwargs)

    def add(self, emitter):
        self.emitter = emitter
        for event in self.events:
            emitter.event_handlers[self.priority][event].append(self)
        return self

    def remove(self, emitter=None):
        emitter = emitter or self.emitter

        for event in self.events:
            emitter.event_handlers[self.priority][event].remove(self)


class Emitter(object):
    def __init__(self, wrapper=None):
        self.wrapper = wrapper
        self.event_handlers = {
            k: defaultdict(list) for k in Priority.attrs.values()
        }

    def _call(self, func, args, kwargs):
        try:
            func(*args, **kwargs)
        except Stop:
            pass

    def emit(self, name, *args, **kwargs):
        for prio in [Priority.BEFORE, Priority.NONE, Priority.AFTER]:
            for listener in self.event_handlers[prio].get(name, []) + self.event_handlers[prio].get('', []):
                if self.wrapper:
                    self.wrapper(self._call, listener, args, kwargs)
                else:
                    self._call(listener, args, kwargs)

    def on(self, *args, **kwargs):
        return EmitterSubscription(args[:-1], args[-1], **kwargs).add(self)

    def once(self, *args, **kwargs):
        from gevent.event import AsyncResult

        result = AsyncResult()
        li = None

        def _f(e):
            result.set(e)
            li.remove()

        li = self.on(*args + (_f, ))

        return result.wait(kwargs.pop('timeout', None))

    def wait(self, *args, **kwargs):
        from gevent.event import AsyncResult

        result = AsyncResult()
        match = args[-1]

        def _f(e):
            if match(e):
                result.set(e)

        return result.wait(kwargs.pop('timeout', None))
