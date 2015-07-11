import json, uuid, logging, thread, time, os, sys, traceback

from flask import current_app

from .slack import SlackMessage

log = logging.getLogger(__name__)

TASKS = {}

def task(*args, **kwargs):
    def deco(f):
        task = Task(current_app.fanny.redis, f.__name__, f, *args, **kwargs)

        if f.__name__ in TASKS:
            raise Exception("Conflicting task name: %s" % f.__name__)

        TASKS[f.__name__] = task
        return task
    return deco

class Task(object):
    def __init__(self, name, f, max_running=None, buffer_time=None, max_size=25):
        self.redis = current_app.fanny.redis
        self.name = name
        self.f = f
        self.max_running = max_running
        self.max_size = max_size
        self.buffer_time = buffer_time

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)

    def queue(self, *args, **kwargs):
        # Make sure we have space
        if (self.redis.llen("jq:%s" % self.name) or 0) > self.max_size:
            raise Exception("Queue for task %s is full!" % self.name)

        id = str(uuid.uuid4())
        self.redis.rpush("jq:%s" % self.name, json.dumps({
            "id": id,
            "args": args,
            "kwargs": kwargs
        }))
        return id

class TaskRunner(object):
    def __init__(self, name, task):
        self.redis = current_app.fanny.redis
        self.name = name
        self.f = task
        self.running = 0

    def process(self, job):
        self.running += 1
        log.info('[%s] Running job %s...', job['id'], self.name)
        self.redis.set("task:%s" % job['id'], 1)
        start = time.time()

        try:
            self.f(*job['args'], **job['kwargs'])
            if self.f.buffer_time:
                time.sleep(self.f.buffer_time)
        except:
            log.exception("[%s] Failed in %ss", job['id'], time.time() - start)

            # Send slack stack trace
            try:
                exc_type, exc_obj, exc_tb = sys.exc_info()

                content = ''.join(traceback.format_exception(exc_type, exc_obj, exc_tb))
                msg = SlackMessage("Task Exception (%s)" % str(exc_obj), color='danger')
                msg.add_custom_field("Task Name", self.name)
                msg.add_custom_field("Task ID", job['id'])
                msg.add_custom_field("Duration", "%ss" % (time.time() - start))
                msg.add_custom_field("Exception", content)
                msg.send_async()
            except Exception:
                log.exception("Failed to send slack exception trace: ")
        finally:
            self.redis.delete("task:%s" % job['id'])
            self.running -= 1
        log.info('[%s] Completed in %ss', job['id'], time.time() - start)

    def run(self, job):
        if self.f.max_running:
            while self.f.max_running <= self.running:
                time.sleep(.5)

        thread.start_new_thread(self.process, (job, ))

class TaskManager(object):
    def __init__(self, redis):
        self.redis = redis
        self.load()
        self.queues = ["jq:" + i for i in TASKS.keys()]
        self.runners = {k: TaskRunner(self.redis, k, v) for k, v in TASKS.items()}
        self.active = True

    def load(self):
        for f in os.listdir("tasks/"):
            if f.endswith(".py"):
                __import__("tasks." + f.rsplit(".")[0])

    def run(self):
        log.info("Running TaskManager on %s queues...", len(self.queues))
        while self.active:
            chan, job = self.redis.blpop(self.queues)
            job_name = chan.split(":", 1)[1]
            job = json.loads(job)

            if job_name not in TASKS:
                log.error("Cannot handle task %s",job_name)
                continue

            self.runners[job_name].run(job)

