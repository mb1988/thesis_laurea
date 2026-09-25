# -*- coding: utf-8 -*-
"""Run the 2014 `thesis_laurea` app on Python 3.14.

The original project targets Python 2.7 with Flask 0.10-era dependencies
(``flask.ext.*`` imports, Flask-WTF 0.x field names, Flask-MongoEngine,
Flask-WeasyPrint, Flask-Script, PostgreSQL).  Its own code is plain enough to
run unchanged on a modern interpreter -- what broke is the dependency APIs.

This module (imported *before* ``app``):

* fills in the env vars ``config.py`` expects (``DATABASE_URL``,
  ``STACKATO_FILESYSTEM``, ``PORT``) and switches the working directory to the
  repo root, because the questionnaire JSON files are opened by relative path;
* registers ``flask.ext.<name>`` aliases pointing at the modern packages, plus
  the small shims in ``dev/compat``;
* imports and exposes the Flask app.

Nothing here is needed for a "real" deployment; it exists so the thesis project
can be started locally with ``python dev/run.py``.
"""

import os
import sys
import types
from pathlib import Path

DEV_DIR = Path(__file__).resolve().parent
REPO_ROOT = DEV_DIR.parent
COMPAT_DIR = DEV_DIR / "compat"

for _path in (str(COMPAT_DIR), str(REPO_ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# config.py reads these straight from the environment (Stackato used to inject
# them), and the questionnaire JSON files are opened by relative path.
os.chdir(str(REPO_ROOT))

_instance_dir = REPO_ROOT / "instance"
_instance_dir.mkdir(exist_ok=True)
_filesystem_dir = DEV_DIR / "filesystem"
(_filesystem_dir / "upload").mkdir(parents=True, exist_ok=True)

os.environ.setdefault("PORT", "5000")
os.environ.setdefault("HOST", "127.0.0.1")
os.environ.setdefault(
    "DATABASE_URL", "sqlite:///" + (_instance_dir / "dev.sqlite3").as_posix()
)
os.environ.setdefault("STACKATO_FILESYSTEM", str(_filesystem_dir))
# mongomock:// keeps documents in memory, so no MongoDB server is required to
# try the app.  Point MONGO_URI at mongodb://localhost:27017 for a real server.
os.environ.setdefault("MONGO_URI", "mongomock://localhost")
os.environ.setdefault("MONGO_DB", "asl")


def _register_flask_ext_aliases():
    """Make ``import flask.ext.foo`` resolve to the modern packages."""
    import flask_admin
    import flask_admin.babel
    import flask_admin.base
    import flask_admin.contrib
    import flask_admin.contrib.fileadmin
    import flask_admin.contrib.mongoengine  # noqa: F401 (populates the alias)
    import flask_admin.contrib.sqla
    import flask_admin.form
    import flask_login
    import flask_sqlalchemy

    import shim_mongoengine
    import shim_login
    import shim_script
    import shim_wtf

    ext = types.ModuleType("flask.ext")
    ext.__path__ = []  # marks it as a package so submodule imports work
    sys.modules["flask.ext"] = ext

    def alias(dotted_name, module):
        sys.modules[dotted_name] = module
        parent, _, leaf = dotted_name.rpartition(".")
        setattr(sys.modules[parent], leaf, module)
        return module

    alias("flask.ext.admin", flask_admin)
    alias("flask.ext.admin.babel", flask_admin.babel)
    alias("flask.ext.admin.base", flask_admin.base)
    alias("flask.ext.admin.form", flask_admin.form)
    alias("flask.ext.admin.contrib", flask_admin.contrib)
    # flask_admin renamed its SQLAlchemy integration to contrib.sqla in 1.3.
    alias("flask.ext.admin.contrib.sqlamodel", flask_admin.contrib.sqla)
    alias("flask.ext.admin.contrib.mongoengine", flask_admin.contrib.mongoengine)
    alias("flask.ext.admin.contrib.fileadmin", flask_admin.contrib.fileadmin)
    alias("flask.ext.login", shim_login)
    alias("flask.ext.mongoengine", shim_mongoengine)
    alias("flask.ext.mongoengine.wtf", shim_mongoengine)
    alias("flask.ext.mongoengine.wtf.fields", shim_mongoengine)
    alias("flask.ext.script", shim_script)
    alias("flask.ext.sqlalchemy", flask_sqlalchemy)
    alias("flask.ext.wtf", shim_wtf)


_register_flask_ext_aliases()

from app import app as flask_app  # noqa: E402  (must come after the aliases)

__all__ = ["flask_app", "REPO_ROOT"]


if __name__ == "__main__":
    print("flask.ext shims installed; app imported as 'flask_app'")
    print("database: %s" % os.environ["DATABASE_URL"])
    print("mongo:    %s" % os.environ["MONGO_URI"])
