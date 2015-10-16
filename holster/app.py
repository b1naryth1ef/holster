import sys, os

from flask import current_app
from redis import Redis

from .filters import register_filters
from .log import setup_logging
from .session import SessionProvider

class Holster(object):
    def __init__(self, app=None, auto_load_views=True):
        self.app = app or current_app
        self.redis = None

        self.init_app(self.app)

        if auto_load_views:
            self.load_views()

        if "REDIS" in self.app.config:
            self.init_redis(self.app.config.get("REDIS"))
            self.sessions = SessionProvider(self.redis)
            self.app.sessions = self.sessions

    def init_redis(self, kwargs):
        self.redis = Redis(**kwargs)

    def init_app(self, app):
        app.holster = self
        register_filters(app)
        setup_logging(app)

    def load_views(self):
        for view in os.listdir("views"):
            if not view.endswith(".py") or view.startswith("_"):
                continue

            view = "views." + view.split(".py")[0]
            __import__(view)
            self.app.register_blueprint(getattr(sys.modules[view], view.split(".")[-1]))

