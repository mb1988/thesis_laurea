# Running thesis_laurea locally

`thesis_laurea` (2014) is an ASL addictions-service admin: Flask + Flask-Admin
for the CRUD screens, MongoDB documents for centri/medici/pazienti and the
EuropASI questionnaires, a SQL table for the login users, and PDF export of the
questionnaires. It was deployed to Stackato with a PostgreSQL and a MongoDB
service.

The application code is the original one. This folder is only a development
harness that bridges the 2014 dependency APIs to packages that still install
and run in 2026.

Stack verified on 2026-09-25: Windows 11, Python 3.14.3, Flask 3.1.3,
Flask-Admin 2.2.1, WTForms 3.2.2, mongoengine 0.29.3, mongomock 4.3.0
(see `requirements.txt`).

## Quick start

```powershell
cd thesis_laurea

# once: virtualenv + dependencies (or: pip install -r requirements.txt)
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# once: the users table (admin/password, guest/password)
.\.venv\Scripts\python.exe dev\setup_db.py

# every time: start the server
.\.venv\Scripts\python.exe dev\run.py
```

Then open <http://127.0.0.1:5000/> and log in as **admin** / **password**
(`guest` exists too, with `admin = False`).

`python run.py` and `python manage.py setup` also work: both import
`dev/bootstrap.py` when it is present.

## What the original expected, and what we do instead

| Original (2014) | Now |
| --- | --- |
| Python 2.7 | Python 3.14 in `.venv/` |
| `flask.ext.sqlalchemy`, `flask.ext.login`, `flask.ext.admin`, `flask.ext.wtf`, `flask.ext.script` | aliased to the modern packages by `bootstrap.py` |
| Flask-WTF 0.x (`TextField`, `required()`) | `compat/shim_wtf.py` |
| flask-login 0.2 (methods) | `compat/shim_login.py` (0.6 turned them into properties) |
| flask-mongoengine 0.x | `compat/shim_mongoengine.py` (plain mongoengine + `QuerySetSelectField`) |
| Flask-Script | `compat/shim_script.py` (runs commands in an app context) |
| Flask-WeasyPrint (needs GTK/Pango) | `compat/flask_weasyprint.py` -> real WeasyPrint, else xhtml2pdf, else HTML |
| PostgreSQL via `DATABASE_URL` | SQLite `instance/dev.sqlite3` |
| MongoDB database `asl` | mongomock, in memory (`MONGO_URI`) |
| `STACKATO_FILESYSTEM` upload folder | `dev/filesystem/upload` |

## Changes made to the original sources

Everything here is mechanical; no feature was added or removed.

| File(s) | Change | Why |
| --- | --- | --- |
| 13 modules under `app/`, plus `config.py` and `manage.py` | tabs expanded to spaces (`dev/tools/expandtabs.py`) | Python 3 raises `TabError` on the tab/space mixes Python 2 allowed. Tabs expand at 8 columns, i.e. exactly what Python 2 computed, so the original block structure is preserved. |
| `config.py` | `environ.get(...)` with local defaults, `WTF_CSRF_ENABLED = False` | Stackato used to inject `DATABASE_URL` / `STACKATO_FILESYSTEM`; the 2014 templates have no CSRF token field. |
| `run.py` | host/port read with defaults | was `app.run('0.0.0.0', int(environ['PORT']))`. |
| `run.py`, `manage.py` | import `dev/bootstrap.py` if present | so the original entry points work on modern Python. |
| 4 `list*.html` templates | dropped the `new AdminFilters(...)` JS block | it used `admin_view._filter_dict` / `filter_data` / `filter_types`, which flask-admin removed (it ships its own filter widget now). |
| `layout.html` | every asset via `url_for`, jQuery path fixed | it pointed at `/static/js/jquery-1.9.0.js`, which does not exist (the file is `js/jquery.js`), and used relative paths that break outside `/`. |
| 8 admin templates | dropped `select2/select2.css`, `css/datepicker.css`, `js/bootstrap-datepicker.js`, `js/bootstrap-tooltip.js` | those files no longer ship with flask-admin; the reference is now the real `vendor/select2/select2.css`. |
| `app/admin/forms.py` | fixed `MyModelAdmin.is_accessible` | see "Bug fixed" below. |
| `requirements.txt` | rewritten for the 2026 stack | the 2014 pins live on in `requirements-2014.txt`. |

## Bug fixed

`MyModelAdmin.is_accessible` (the admin-only Users screen) had `return True` and
`return False` at the same indentation, so the method returned `False` for
admins and `None` otherwise - the screen answered 403 for everybody, including
`admin`. Python 2 read the tab/space mix exactly the same way, so this was an
original bug rather than a porting artefact; it is now the intended check
(admin + authenticated -> True), and `/admin/user/` is reachable as `admin` and
still 403 for `guest`.

## Data and persistence

Mongo is **mongomock** (in memory), so `dev/run.py` snapshots it to
`instance/mongo-asl.json` after each write (throttled to every couple of
seconds) and on exit, and loads that snapshot on the next start. Your data
therefore survives a normal stop/start - but not a hard kill of the process,
and the snapshot is a dev convenience, not a database.

On an empty database `dev/run.py` also seeds one centro, medico, paziente and
the three documents (`DEV_SEED=0` disables that, `DEV_PERSIST=0` turns off the
snapshot entirely).

To keep real data, point the app at a MongoDB server - nothing else changes:

```powershell
$env:MONGO_URI = 'mongodb://localhost:27017'
$env:DEV_SEED = '0'
.\.venv\Scripts\python.exe dev\run.py
```

The SQL users table is already persistent (`instance/dev.sqlite3`).

## Environment variables

| Variable | Default | Notes |
| --- | --- | --- |
| `MONGO_URI` | `mongomock://localhost` | `mongodb://localhost:27017` for a real server |
| `MONGO_DB` | `asl` | database name |
| `DATABASE_URL` | `sqlite:///instance/dev.sqlite3` | SQLAlchemy URI for the users table |
| `PORT` / `HOST` | `5000` / `127.0.0.1` | |
| `DEV_RELOAD` | `1` | auto-reloader, `0` to disable |
| `DEV_SEED` | `1` | seed demo data at startup, `0` to disable |
| `DEV_PERSIST` | `1` | snapshot/restore the in-memory Mongo, `0` to disable |
| `SQLALCHEMY_ECHO` | `1` | was hard-coded `True`; `0` silences the SQL log |

## Developer scripts

```powershell
.\.venv\Scripts\python.exe dev\smoke_test.py   # login + GET every page (expects no 4xx/5xx)
.\.venv\Scripts\python.exe dev\demo_data.py    # create sample data through the admin forms
.\.venv\Scripts\python.exe dev\mongo_store.py  # show|save|load the dev Mongo snapshot
.\.venv\Scripts\python.exe dev\tools\expandtabs.py --check
```

## Quirks in the original code (kept as-is)

* Passwords are stored in clear text and compared with `!=` (`app/user/forms.py`).
  That is the 2014 design; do not reuse these accounts anywhere real.
* `MyFileAdmin` is mounted at `/admin/myfileadmin/`, not `/admin/upload/`
  (flask-admin derives the endpoint from the class name).
* The upload folder is created at import time from `DOWNLOAD_FOLDER`.
