import sys, os

from flask import current_app

from .filters import register_filters
from .log import setup_logging
from .session import SessionProvider


class ViewFinder(object):
    @staticmethod
    def get_views_path():
        """
        Walks current path to find the views directory
        """
        for root, dirs, files in os.walk(os.getcwd()):
            if root.endswith("views"):
                return root

    @classmethod
    def get_views(cls):
        """
        Returns all views that should be loaded
        """
        views_path = cls.get_views_path()
        if not views_path:
            raise Exception('Failed to locate views directory')

        module = views_path.replace(os.getcwd(), '').replace('/', '.')[1:]
        for view in os.listdir(views_path):
            if not view.endswith(".py") or view.startswith("_"):
                continue

            view = module + "." + view.split(".py")[0]
            __import__(view)
            yield getattr(sys.modules[view], view.split(".")[-1])


class Holster(object):
    def __init__(self, app=None, auto_load_views=True, use_sessions=False):
        self.auto_load_views = auto_load_views

        self.app = app or current_app
        if self.app:
            self.init_app(self.app)

        # Optionally initialize redis
        self.redis = None

        # Initialize redis if its in our app config
        if 'REDIS' in self.app.config:
            self.init_redis(self.app.config.get("REDIS"))

        # Initialize sessions if we have redis and want to use them
        if self.redis and use_sessions:
            self.sessions = SessionProvider(self.redis)
            self.app.sessions = self.sessions

    def init_app(self, app):
        app.holster = self
        register_filters(app)
        setup_logging(app)

        if self.auto_load_views:
            map(self.app.register_blueprint, ViewFinder.get_views())

    def init_redis(self, kwargs):
        from redis import Redis
        self.redis = Redis(**kwargs)
