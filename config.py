from os import environ, urandom
from os.path import join
from tempfile import gettempdir

SECRET_KEY = urandom( 24 )

# Stackato used to inject DATABASE_URL / STACKATO_FILESYSTEM; dev/bootstrap.py
# provides local fallbacks so the app can also run straight from a checkout.
SQLALCHEMY_DATABASE_URI = environ.get( 'DATABASE_URL', 'sqlite://' )
# Was a hard-coded True; keep it for debugging but allow SQLALCHEMY_ECHO=0.
SQLALCHEMY_ECHO = environ.get( 'SQLALCHEMY_ECHO', '1' ) == '1'
MONGODB_SETTINGS = {
        'db': environ.get( 'MONGO_DB', 'asl' ),
        'host': environ.get( 'MONGO_URI', 'localhost' ),
}
DOWNLOAD_FOLDER = join( environ.get( 'STACKATO_FILESYSTEM', gettempdir() ), 'upload' )

# The 2014 templates predate Flask-WTF's CSRF token field.
WTF_CSRF_ENABLED = False
