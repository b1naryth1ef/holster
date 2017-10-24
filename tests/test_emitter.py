from gevent.monkey import patch_all
patch_all()  # noqa: E402

import time

from gevent.event import AsyncResult
from holster.emitter import Emitter, Priority


def test_emitter_spawn():
    emitter = Emitter(spawn_each=True)

    class TestEvent(object):
        pass

    def handler_a(event):
        time.sleep(1)
        event.value = 1

    def handler_b(event):
        time.sleep(1)
        event.value = 2

    def handler_c(event):
        event.result.set(event.value)

    event = TestEvent()
    event.value = 0
    event.result = AsyncResult()

    emitter.on('test', handler_a, priority=Priority.BEFORE)
    emitter.on('test', handler_b)
    emitter.on('test', handler_c, priority=Priority.AFTER)
    emitter.emit('test', event)

    assert event.result.wait() == 2
