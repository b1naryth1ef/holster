import json, time, logging

from flask import current_app

from uuid import uuid4
from flask import request

log = logging.getLogger(__name__)

# 5 days
DEFAULT_SESSION_TTL = 60 * 60 * 24 * 5


def find_sessions_for_user(uid):
    """
    Attempts to find all sessions associated with a user.
    """
    for key in current_app.holster.redis.keys("session:*"):
        sess = Session(key.split(":")[1])
        if sess['u'] == uid:
            yield sess


class SessionProvider(object):
    def __init__(self, redis, ttl=DEFAULT_SESSION_TTL):
        self.redis = redis
        self.ttl = ttl

    def get(self, id=None):
        return Session(self, id)


class Session(object):
    def __init__(self, provider, id=None):
        self.provider = provider
        self.prefix = "session:{}:{}".format(provider, '{}')
        self._id = None
        self._data = {}
        self._changed = False

        # Try to load a previous session
        id = id or request.cookies.get("s")
        data = self.provider.redis.get(self.prefix.format(id))
        if data:
            self._data = json.loads(data)
            self._id = id

    @property
    def key(self):
        return self.prefix.format(self._id)

    @property
    def new(self):
        return not self._id

    def delete(self):
        self.provider.redis.delete(self.key)
        self._data = {}
        self._id = None
        self._changed = False

    def get(self, key, default=None):
        if key in self._data:
            return self[key]
        return default

    def __delitem__(self, item):
        self._changed = True
        del self._data[item]

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, item, value):
        self._changed = True
        self._data[item] = value

    def save(self, response):
        if not self._changed:
            return False

        # Get current TTL
        self._id = self._id or str(uuid4())
        ttl = int(self.provider.redis.ttl(self.key) or self.provider.ttl)

        # Set cookie and key
        self.provider.redis.set(self.key, json.dumps(self._data))
        self.provider.redis.expire(self.key, ttl if ttl != -1 else self.provider.ttl)
        response.set_cookie("s", self._id, expires=(time.time() + ttl))
        return True
