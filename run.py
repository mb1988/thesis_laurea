try:
    # Local development entry point: registers the flask.ext.* compatibility
    # shims in dev/bootstrap.py.  Absent in a "vanilla" checkout, hence the
    # try/except.
    from dev import bootstrap  # noqa: F401
except ImportError:
    pass

from os import environ

from app import app

app.debug = True
# Was app.run( '0.0.0.0', int( environ[ 'PORT' ] ) ): the host env var and the
# defaults let the app start locally without the Stackato environment.
app.run( environ.get( 'HOST', '127.0.0.1' ), int( environ.get( 'PORT', '5000' ) ) )
