#vengono modificate alcune viste da sqlamodel, admin per far in modo che vi possano accedere solo gli utenti registrati.


from flask.ext.admin.contrib import sqlamodel
from flask.ext.admin.contrib import mongoengine
from flask.ext import admin,login
from flask.ext.admin.contrib.fileadmin import FileAdmin
from flask.ext.admin import expose, BaseView
from flask import url_for, redirect, send_from_directory

from app.user.views import *
from app import app

# Create customized model view class
class MyModelView(mongoengine.ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()

#crea una vista accessibile solo agli utenti amministratori
class MyModelAdmin(sqlamodel.ModelView):
    def is_accessible(self):
        if login.current_user.is_authenticated() and login.current_user.admin:
        	return True
		return False		
		
# Create customized index view class
class MyAdminIndexView(admin.AdminIndexView):
    def is_accessible(self):
        return login.current_user.is_authenticated()

class MyFileAdmin(FileAdmin):
	#modifico il file list in modo tale che se clicco sul file mi porta al download del file e non all'edit
	list_template= 'admin/file/list2.html'
	
	@expose('/download/<path:path>')
	def download_file(self,path=None):
		return send_from_directory(app.config['DOWNLOAD_FOLDER'],
                               path)
	
	def is_accessible(self):
		return login.current_user.is_authenticated()
   

class Logout(BaseView):
	@expose('/')
	def log_out(self):
		return redirect(url_for('users.logout_view'))
	
	def is_accessible(self):
		return login.current_user.is_authenticated()
