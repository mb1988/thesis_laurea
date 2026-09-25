# -*- coding: utf-8 -*-
"""``flask.ext.mongoengine`` shim (replaces flask-mongoengine).

flask-mongoengine 1.0 imports ``flask.json.JSONEncoder``, which Flask removed
in 2.3, so it cannot even be imported on a modern Flask.  The app only uses a
small slice of it:

    db = MongoEngine(app)      -> connect using app.config['MONGODB_SETTINGS']
    db.Document / db.StringField / db.ReferenceField / ...  (mongoengine classes)
    flask.ext.mongoengine.wtf.fields.QuerySetSelectField

All of that is provided here on top of plain mongoengine.  Set ``MONGO_URI`` to
a real ``mongodb://`` server, or leave it as ``mongomock://`` to run against an
in-memory Mongo (mongomock) with no server installed.
"""

import mongoengine
from mongoengine import *  # noqa: F401,F403  (Document, fields, ...)
from wtforms import widgets
from wtforms.fields import SelectFieldBase
from wtforms.validators import ValidationError

__all__ = ["MongoEngine", "QuerySetSelectField"]


class MongoEngine(object):
    """Minimal stand-in for flask_mongoengine.MongoEngine."""

    def __init__(self, app=None):
        self.app = None
        self.connection = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        settings = dict(app.config.get("MONGODB_SETTINGS") or {})

        alias = settings.pop("alias", "default")
        db_name = settings.pop("db", None) or settings.pop("DB", None) or app.name
        host = settings.pop("host", None) or settings.pop("HOST", None) or "localhost"
        port = int(settings.pop("port", 27017))

        if host.startswith("mongomock://"):
            import mongomock
            host, port = "localhost", 27017
            settings["mongo_client_class"] = mongomock.MongoClient

        self.connection = mongoengine.connect(
            db=db_name, alias=alias, host=host, port=port, **settings
        )
        app.extensions["mongoengine"] = self
        return self.connection


def _mirror_mongoengine_names():
    """Expose ``db.<Field>`` the way flask-mongoengine did."""
    for name in dir(mongoengine):
        if not name.startswith("_") and not hasattr(MongoEngine, name):
            setattr(MongoEngine, name, getattr(mongoengine, name))


_mirror_mongoengine_names()


class QuerySetSelectField(SelectFieldBase):
    """Pick a mongoengine document (used for the paziente selector)."""

    widget = widgets.Select()

    def __init__(self, label=None, validators=None, queryset=None,
                 label_attr="", allow_blank=False, blank_text="", **kwargs):
        super(QuerySetSelectField, self).__init__(label, validators, **kwargs)
        self.queryset = queryset
        self.label_attr = label_attr
        self.allow_blank = allow_blank
        self.blank_text = blank_text
        self._object_list = None

    def _get_object_list(self):
        if self._object_list is None:
            self._object_list = [(str(doc.pk), doc) for doc in self.queryset]
        return self._object_list

    def iter_choices(self):
        # WTForms 3.1+ passes (value, label, selected, render_kw) to the widget.
        if self.allow_blank:
            yield ("__None", self.blank_text, self.data is None, {})
        for pk, obj in self._get_object_list():
            yield (pk, self.get_label(obj), obj == self.data, {})

    def process_formdata(self, valuelist):
        if not valuelist:
            return
        if valuelist[0] == "__None":
            self.data = None
            return
        for pk, obj in self._get_object_list():
            if valuelist[0] == pk:
                self.data = obj
                return
        for doc in self.queryset:
            if str(doc.pk) == valuelist[0]:
                self.data = doc
                return
        raise ValueError(self.gettext("Not a valid choice"))

    def process_data(self, value):
        self.data = value

    def pre_validate(self, form):
        if not self.allow_blank or self.data is not None:
            for _pk, obj in self._get_object_list():
                if self.data == obj:
                    return
            raise ValidationError(self.gettext("Not a valid choice"))

    def get_label(self, doc):
        if doc is None:
            return u""
        if self.label_attr:
            return getattr(doc, self.label_attr)
        # The models define __unicode__ (Python 2 heritage) for their labels.
        legacy = getattr(doc, "__unicode__", None)
        if legacy is not None:
            try:
                return legacy()
            except Exception:
                pass
        return str(doc)
