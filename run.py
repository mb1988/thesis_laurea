from os import environ

from app import app

app.debug = True
app.run( '0.0.0.0', int( environ[ 'PORT' ] ) )
