# coding:utf-8

import os
import logging
from logging.handlers import RotatingFileHandler
from .settings import basedir


def init_app_logger(app, log_filename):
    log_file = os.path.join(basedir, "logs", log_filename)
    if not os.path.exists(os.path.dirname(log_file)):
        os.mkdir(os.path.dirname(log_file))

    file_handler = RotatingFileHandler(log_file, "a", 1 * 1024 * 1024, 5)
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"))
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)
