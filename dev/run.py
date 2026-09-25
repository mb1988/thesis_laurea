# -*- coding: utf-8 -*-
"""Start the thesis_laurea app locally:  python dev/run.py

Equivalent to the original ``python run.py``, but with the compatibility
bootstrap applied first, without requiring the Stackato env vars, and with the
in-memory Mongo snapshotted to instance/ so your data survives a restart.
"""

import atexit
import os
import time

import bootstrap  # noqa: F401  installs the shims and the env defaults

import mongo_store
from app import app

SAVE_EVERY_SECONDS = 2


def seed_if_empty():
    """Give the in-memory demo Mongo something to look at.

    mongomock starts empty on every process, so without this the admin lists
    would be blank.  Set DEV_SEED=0 to start with an empty database.
    """
    from app.admin.centro.models import Centro

    if Centro.objects.count():
        return
    import demo_data

    with app.test_client() as client:
        demo_data.seed(client, verbose=True)


def enable_persistence():
    """Snapshot the dev Mongo on exit, and at most every few seconds."""
    restored, path = mongo_store.restore()
    print("mongo: restored %d document(s) from %s" % (restored, path))

    last_save = [0.0]

    @app.after_request
    def _autosave(response):
        now = time.time()
        if now - last_save[0] > SAVE_EVERY_SECONDS:
            last_save[0] = now
            try:
                mongo_store.save()
            except Exception as error:  # never break a request because of this
                print("mongo: autosave failed: %s" % error)
        return response

    def _final_save():
        try:
            count, saved_to = mongo_store.save()
            print("mongo: saved %d document(s) to %s" % (count, saved_to))
        except Exception as error:
            print("mongo: final save failed: %s" % error)

    atexit.register(_final_save)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    host = os.environ.get("HOST", "127.0.0.1")
    use_reloader = os.environ.get("DEV_RELOAD", "1") != "0"
    # With the reloader the script runs twice; only the child serves requests
    # and only it should touch the on-disk snapshot.
    reloader_parent = use_reloader and not os.environ.get("WERKZEUG_RUN_MAIN")

    if not reloader_parent:
        if os.environ.get("DEV_PERSIST", "1") != "0":
            enable_persistence()
        if os.environ.get("DEV_SEED", "1") != "0":
            seed_if_empty()
            if os.environ.get("DEV_PERSIST", "1") != "0":
                mongo_store.save()

    print("\n  ASL admin on http://%s:%s/  (login: admin / password)\n" % (host, port))
    app.run(
        host=host,
        port=port,
        debug=True,
        use_reloader=use_reloader,
    )
