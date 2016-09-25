import time, logging, signal, sys, os

from flask import current_app

from dateutil.relativedelta import relativedelta
from datetime import datetime

log = logging.getLogger(__name__)


class Task(object):
    def __init__(self, task, now, delta):
        self.redis = current_app.holster.redis
        self.task = task
        self.delta = delta
        self.last = (datetime.utcnow() - relativedelta(years=5)) if now else datetime.utcnow()
        self.last_id = None
        self.last_check = time.time()

    def is_running(self):
        if self.last_id:
            if (time.time() - self.last_check) < 5:
                return True

            self.last_check = time.time()
            res = bool(self.redis.exists("task:%s" % self.last_id))
            if not res:
                self.last_id = None
            return res

    def is_active(self):
        return True

    def should_run(self):
        return (self.is_active() and not self.is_running() and
            (datetime.utcnow() > (self.last + self.delta)))

    def run(self):
        log.info("Queueing scheduled task %s" % self.task.name)
        self.last_id = self.task.queue()
        self.last = datetime.utcnow()


class Scheduler(object):
    def __init__(self, pidfile="/tmp/scheduler.pid"):
        self.redis = current_app.holster.redis
        # Write PID to a file
        try:
            with open(pidfile, "w") as f:
                f.write(str(os.getpid()))
        except:
            log.exception("Failed to create PID file: ")

        self.schedules = []
        self.paused = False

        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGHUP, self.handle_signal)

    def handle_signal(self, signum, handler):
        log.info("Handling signal %s" % signum)
        sys.exit(0)

    def schedule(self, f, start_now=False, **kwargs):
        self.schedules.append(Task(f, start_now, relativedelta(**kwargs)))

    def run(self):
        log.info("Starting Scheduler...")
        while True:
            time.sleep(.3)
            if self.paused:
                continue

            for task in self.schedules:
                if task.should_run():
                    task.run()
