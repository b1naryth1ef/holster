from gevent.monkey import patch_all
patch_all()  # noqa: E402

import time
import random

from gevent.event import AsyncResult
from holster.emitter import Emitter, Priority


def test_emitter_before():
    emitter = Emitter()

    class TestEvent(object):
        pass

    def handler_before(event):
        time.sleep(1)
        event.value = 1

    def handler_default(event):
        event.result.set(event.value)

    event = TestEvent()
    event.result = AsyncResult()

    emitter.on('test', handler_before, priority=Priority.BEFORE)
    emitter.on('test', handler_default)
    emitter.emit('test', event)

    assert event.result.wait() == 1


def test_emitter_sequential():
    emitter = Emitter()

    class TestEvent(object):
        pass

    def handler_contained(event):
        time.sleep(random.randint(1, 100) / 100)
        event.value += 1
        event.order.append(event.value)

        if event.value == 3:
            event.result.set()

    event = TestEvent()
    event.order = []
    event.value = 0
    event.result = AsyncResult()

    emitter.on('test', handler_contained, priority=Priority.SEQUENTIAL)
    emitter.emit('test', event)
    emitter.emit('test', event)
    emitter.emit('test', event)

    event.result.wait()
    assert event.order == [1, 2, 3]
    assert event.value == 3
