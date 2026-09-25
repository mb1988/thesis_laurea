#vengono modificate alcune viste da sqlamodel, admin per far in modo che vi possano accedere solo gli utenti registrati.


from flask.ext.admin.contrib import sqlamodel
from flask.ext.admin.contrib import mongoengine
from flask.ext import admin,login
from flask.ext.admin.contrib.fileadmin import FileAdmin
from flask.ext.admin import expose, BaseView
from flask import url_for, redirect, send_from_directory

from app.user.views import *
from app import app


class LoginRequiredView(object):
    """Chi non ha fatto il login viene portato alla pagina di accesso.

    Senza questo, flask-admin risponde con un 403 nudo: per un applicativo
    reale e' meglio riportare l'utente al login.
    """

    def inaccessible_callback(self, name, **kwargs):
        if not login.current_user.is_authenticated():
            return redirect(url_for('users.index'))
        return super(LoginRequiredView, self).inaccessible_callback(name, **kwargs)


# Create customized model view class
class MyModelView(LoginRequiredView, mongoengine.ModelView):

    # esportazione CSV/JSON degli elenchi e paginazione fissa
    can_export = True
    page_size = 20

    def is_accessible(self):
        return login.current_user.is_authenticated()


#crea una vista accessibile solo agli utenti amministratori
class MyModelAdmin(LoginRequiredView, sqlamodel.ModelView):

    can_export = True
    page_size = 20

    def is_accessible(self):
        if login.current_user.is_authenticated() and login.current_user.admin:
            return True
        return False


# Create customized index view class
class MyAdminIndexView(LoginRequiredView, admin.AdminIndexView):
    """Home dell'area riservata: dashboard con i numeri del servizio."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('name', 'Dashboard')
        kwargs.setdefault('menu_icon_type', 'fa')
        kwargs.setdefault('menu_icon_value', 'fa-dashboard')
        super(MyAdminIndexView, self).__init__(*args, **kwargs)

    def is_accessible(self):
        return login.current_user.is_authenticated()

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated():
            return redirect(url_for('users.index'))
        # importato qui per non creare cicli di import all'avvio
        from app.admin.dashboard import build_context
        return self.render('admin/index.html', **build_context())


class MyFileAdmin(LoginRequiredView, FileAdmin):
    # l'elenco file di flask-admin 2.x collega gia' il nome del file al
    # download, quindi non serve piu' il template personalizzato del 2014
    # (admin/file/list2.html), che usava una struttura di 'items' non piu'
    # esistente.

    def is_accessible(self):
        return login.current_user.is_authenticated()


class Logout(LoginRequiredView, BaseView):
    @expose('/')
    def log_out(self):
        return redirect(url_for('users.logout_view'))

    def is_accessible(self):
        return login.current_user.is_authenticated()

    def is_visible(self):
        # il pulsante "Esci" e' gia' nella barra di navigazione
        return False
