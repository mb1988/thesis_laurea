#questo file inizializa l'applicazione

from flask import  Flask, url_for, redirect, render_template, request, send_from_directory
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)

app.config.from_object('config')

db = MongoEngine(app)
dbsqla = SQLAlchemy(app)

@app.errorhandler(404)
def not_found(error):
	return render_template('404.html'), 404
		

from app.user.views import users
app.register_blueprint(users)
