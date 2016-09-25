import json, uuid, logging, thread, time, os

log = logging.getLogger(__name__)

_TASKS = {}
_manager = None


def task(*args, **kwargs):
    """
    Decorator which creates and registers a new task
    """
    def deco(f):
        task = Task(f.__name__, f, *args, **kwargs)

        if f.__name__ in _TASKS:
            raise Exception("Conflicting task name: %s" % f.__name__)

        _TASKS[f.__name__] = task
        return task
    return deco


class Task(object):
    def __init__(self, name, f, max_running=None, buffer_time=None, max_size=25):
        self.name = name
        self.f = f
        self.max_running = max_running
        self.max_size = max_size
        self.buffer_time = buffer_time

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)

    def queue(self, *args, **kwargs):
        if _manager.get_queue_length(self.name) > self.max_size:
            raise Exception('Queue for task {} is full'.format(self.name))

        return _manager.add_job(self.name, {
            'id': id,
            'args': args,
            'kwargs': kwargs,
        })


class TaskRunner(object):
    def __init__(self, manager, name, task):
        self.manager = manager
        self.name = name
        self.f = task
        self.running = 0

    def process(self, job):
        self.running += 1
        log.info('[%s] Running job %s...', job['id'], self.name)
        self.manager.track_job_start(job)
        start = time.time()

        try:
            self.f(*job['args'], **job['kwargs'])
            if self.f.buffer_time:
                time.sleep(self.f.buffer_time)
        except:
            log.exception("[%s] Failed in %ss", job['id'], time.time() - start)
        finally:
            self.manager.track_job_end(job)
            self.running -= 1

        log.info('[%s] Completed in %ss', job['id'], time.time() - start)

    def run(self, job):
        if self.f.max_running:
            while self.f.max_running <= self.running:
                time.sleep(.5)

        thread.start_new_thread(self.process, (job, ))


class TaskManager(object):
    def __init__(self, redis=None, autoload=True):
        # If no global manager has been created, set us to it
        global _manager
        if not _manager:
            _manager = self

        self.redis = redis
        self.queue = None
        self.runners = {k: TaskRunner(self, k, v) for k, v in _TASKS.items()}
        self.active = True

        # Load tasks modules to register tasks
        if autoload:
            self.load()

    def add_job(self, name, job):
        id = str(uuid.uuid4())

        if self.redis:
            self.redis.rpush('jq:%s' % name, json.dumps(job))
        else:
            self.queue.put((name, job))

        return id

    def track_job_start(self, job):
        self.redis.set("task:%s" % job['id'], 1)

    def track_job_end(self, job):
        self.redis.delete("task:%s" % job['id'])

    def load(self):
        for f in os.listdir("tasks/"):
            if f.endswith(".py"):
                __import__("tasks." + f.rsplit(".")[0])

    def run_forever(self):
        from gevent import spawn
        spawn(self.run)

    def run_redis(self):
        queues = ['jq:' + i for i in _TASKS.keys()]

        while self.active:
            chan, job = self.redis.blpop(queues)
            job_name = chan.split(":", 1)[1]
            job = json.loads(job)

            if job_name not in _TASKS:
                log.error('Cannot handle task %s', job_name)
                continue

            self.runners[job_name].run(job)

    def run_gevent(self):
        import gevent
        self.queue = gevent.queue.Queue()

        while self.active:
            job_name, job = self.queue.get()

            if job_name not in self.runners:
                log.error('Cannot handle task %s', job_name)
                continue

            gevent.spawn(self.runners[job_name].run, job)

    def run(self):
        log.info("Running TaskManager on %s queues...", len(self.queues))

        if self.redis:
            return self.run_redis()
        else:
            return self.run_gevent()
