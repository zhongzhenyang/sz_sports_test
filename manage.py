# coding:utf-8
# add some comments

from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

from sz_webapp.core import db
from sz_webapp.frontend import create_app

app = create_app()
migrate = Migrate(app, db)
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


if __name__ == "__main__":
    manager.run()
