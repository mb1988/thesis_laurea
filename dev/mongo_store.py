# -*- coding: utf-8 -*-
"""Save/restore the development Mongo data.

The default ``MONGO_URI`` is mongomock, which keeps documents in memory: stop
the server and everything is gone.  This module snapshots the database to
``instance/mongo-<db>.json`` (BSON JSON, so ObjectId / datetime / DBRef survive)
and loads it back on the next start.  ``dev/run.py`` wires it up; it is also
usable on its own:

    python dev/mongo_store.py save|load|show

Set ``DEV_PERSIST=0`` to work purely in memory.
"""

import sys
from pathlib import Path

from bson import json_util

DEV_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = DEV_DIR.parent / "instance"


def dump_path(db_name):
    return INSTANCE_DIR / ("mongo-%s.json" % db_name)


def _db():
    from mongoengine.connection import get_db

    return get_db()


def save(path=None):
    """Snapshot every non-empty collection.  Returns (documents, path)."""
    db = _db()
    collections = {
        name: list(db[name].find())
        for name in db.list_collection_names()
    }
    collections = {name: docs for name, docs in collections.items() if docs}

    target = Path(path) if path else dump_path(db.name)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json_util.dumps(collections), encoding="utf-8")
    return sum(len(docs) for docs in collections.values()), target


def restore(path=None):
    """Load a snapshot, but never overwrite collections that already exist.

    Returns (documents, path) or (0, path) when there is nothing to load.
    """
    db = _db()
    target = Path(path) if path else dump_path(db.name)
    if not target.exists():
        return 0, target

    collections = json_util.loads(target.read_text(encoding="utf-8"))
    restored = 0
    for name, docs in collections.items():
        if not docs or db[name].count_documents({}):
            continue
        db[name].insert_many(docs)
        restored += len(docs)
    return restored, target


def stats():
    db = _db()
    return {name: db[name].count_documents({}) for name in db.list_collection_names()}


def main(argv):
    command = argv[0] if argv else "show"
    if command == "save":
        count, path = save()
        print("saved %d document(s) to %s" % (count, path))
    elif command == "load":
        count, path = restore()
        print("restored %d document(s) from %s" % (count, path))
    elif command == "show":
        for name, count in sorted(stats().items()):
            print("%-24s %d" % (name, count))
    else:
        raise SystemExit("usage: python dev/mongo_store.py [save|load|show]")
    return 0


if __name__ == "__main__":
    import bootstrap  # noqa: F401  (env defaults + shims + connection)

    raise SystemExit(main(sys.argv[1:]))
