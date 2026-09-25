# -*- coding: utf-8 -*-
"""``flask.ext.script`` shim: just enough Manager to run ``manage.py setup``.

Flask-Script was abandoned years ago and the original project only uses it to
register one ``setup`` command, so a ~20 line stand-in is enough.

Commands run inside an application context, which Flask-SQLAlchemy 3.x
requires for ``create_all()`` (in 2014 the context was implicit).
"""

import sys

__all__ = ["Manager"]


class Manager(object):
    def __init__(self, app=None):
        self.app = app
        self.commands = {}

    def command(self, func):
        self.commands[func.__name__] = func
        return func

    def run(self, args=None):
        argv = list(sys.argv[1:] if args is None else args)
        if not argv or argv[0] in ("-h", "--help", "help"):
            print("available commands: %s" % ", ".join(sorted(self.commands)))
            return None
        name, rest = argv[0], argv[1:]
        if name not in self.commands:
            raise SystemExit("unknown command %r (try --help)" % name)
        command = self.commands[name]
        if self.app is None:
            return command(*rest)
        with self.app.app_context():
            return command(*rest)
