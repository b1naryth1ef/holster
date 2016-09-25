from __future__ import absolute_import

import logging, os

LEVELS = {
    "urllib3": logging.WARNING,
    "requests": logging.DEBUG,
}

FORMAT = "[%(levelname)s] %(asctime)s - %(name)s:%(lineno)d - %(message)s"


def set_logging_levels():
    for log, lvl in LEVELS.items():
        logging.getLogger(log).setLevel(lvl)


def setup_logging(app):
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    set_logging_levels()

    var_log_path = "/var/log/{}".format(app.logger_name)

    if os.path.exists(var_log_path):
        file_handler = logging.FileHandler(os.path.join(var_log_path, "flask.log"))
    else:
        file_handler = logging.FileHandler('/tmp/{}-flask.log'.format(app.logger_name))

    file_handler.setFormatter(logging.Formatter(FORMAT))

    root = logging.getLogger()
    root.addHandler(file_handler)
