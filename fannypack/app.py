import sys, os
from flask import current_app

from .filters import register_filters
from .logging import setup_logging

class FannyPack(object):
    def __init__(self, app=None):
        self.app = app or current_app

        self.init_app(self.app)
        self.load_views()

    def init_app(self, app):
        register_filters(app)
        setup_logging(app)

    def load_views(self):
        for view in os.listdir("views"):
            if not view.endswith(".py") or view.startswith("_"):
                continue

            view = "views." + view.split(".py")[0]
            __import__(view)
            self.app.register_blueprint(getattr(sys.modules[view], view.split(".")[-1]))

