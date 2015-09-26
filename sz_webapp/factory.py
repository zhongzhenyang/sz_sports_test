# coding:utf-8

import os

from flask import Flask, g, current_app, json
from flask_mail import Mail
from werkzeug.local import LocalProxy
import celery
from .helpers import flask_helper
from .core import db

_logger = LocalProxy(lambda: current_app.logger)


def create_app(package_name, package_path, settings_override=None):
    app = Flask(package_name, instance_relative_config=True)
    app.config.from_object(("sz_webapp.settings"))
    app.config.from_pyfile("config.py", silent=True)

    db.init_app(app)
    flask_helper.register_blueprints(app, package_name, package_path)

    @app.teardown_appcontext
    def shutdown_session(error=None):
        if error is None:
            try:
                db.session.commit()
            except Exception, e:
                db.session.rollback()
                _logger.exception(e)
                error = e
            else:
                callbacks = getattr(g, "on_commit_callbacks", [])
                for callback in callbacks:
                    try:
                        callback()
                    except Exception, e:
                        _logger.exception(e)
        else:
            db.session.rollback()
        db.session.remove()
        return error

    return app


def create_celery_app(app=None):
    app = app or create_app("sz_webapp", os.path.dirname(__file__))
    mail = Mail()
    mail.init_app(app)

    from .logs import init_app_logger

    init_app_logger(app, 'celery_error.log')

    celery_app = celery.Celery(__name__,
                               broker=app.config["CELERY_BROKER_URL"],
                               backend=app.config["CELERY_RESULT_BACKEND"])
    celery_app.conf.update(app.config)
    TaskBase = celery_app.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery_app.Task = ContextTask

    from celery.signals import task_postrun
    from .core import db
    from .models import CeleryTaskLog

    @task_postrun.connect
    def task_postrun_handler(*args, **kwargs):
        task_id = kwargs['task_id']
        task_name = kwargs['task'].name
        task_args = kwargs['args']
        task_kwargs = kwargs['kwargs']
        task_state = kwargs['state']
        task_retval = kwargs['retval']

        task_log = db.session.query(CeleryTaskLog).filter(CeleryTaskLog.id == task_id).first()
        if not task_log:
            task_log = CeleryTaskLog(id=task_id, name=task_name, args=task_args, kwargs=task_kwargs, retries=0)

        if task_state == 'SUCCESS':
            task_log.status = 1
        elif task_state == 'FAILURE':
            task_log.status = -1
        elif task_state == 'RETRY':
            task_log.status = -2
            task_log.retries += 1

        if isinstance(task_retval, basestring):
            task_log.retval = task_retval
        elif isinstance(task_retval, Exception):
            task_log.retval = str(task_retval)
        else:
            try:
                task_log.retval = json.dumps(task_retval)
            except Exception, e:
                task_log.retval = "no_jsonified_object"
                _logger.exception(e)

        db.session.add(task_log)
    return celery_app
