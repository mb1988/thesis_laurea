from os import environ, urandom
from os.path import join

SECRET_KEY = urandom( 24 )
SQLALCHEMY_DATABASE_URI = environ[ 'DATABASE_URL' ]
SQLALCHEMY_ECHO = True
MONGODB_SETTINGS = {'DB': "asl"}
DOWNLOAD_FOLDER = join( environ[ 'STACKATO_FILESYSTEM' ], 'upload' )
