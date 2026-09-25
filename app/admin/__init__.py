#viene inizializzato flask-admin con le viste

from os import makedirs
from os.path import isdir

from flask.ext import admin

from app import db, app, dbsqla
from app.admin.forms import *
from app.admin.centro.forms import CentroAdmin
from app.admin.medico.forms import MedicoAdmin
from app.admin.paziente.forms import PazienteAdmin
from app.admin.documenti.forms import QuestionarioIngressoAdmin,ModuloAdmin, QuestionarioFollowupAdmin

from app.user.models import User
from app.admin.paziente.models import Paziente
from app.admin.medico.models import Medico
from app.admin.centro.models import Centro
from app.admin.documenti.models import Questionario_ingresso,Modulo_CDP, Questionario_followup

path = app.config[ 'DOWNLOAD_FOLDER' ]
if not isdir( path ): makedirs( path )

# Create admin
adm = admin.Admin(app, 'ASL - Servizio Dipendenze', index_view=MyAdminIndexView())
adm.add_view(CentroAdmin(Centro, name='Centri', category='Anagrafiche'))
adm.add_view(MedicoAdmin(Medico, name='Medici', category='Anagrafiche'))
adm.add_view(PazienteAdmin(Paziente, name='Pazienti', category='Anagrafiche'))
adm.add_view(QuestionarioIngressoAdmin(Questionario_ingresso,name='Questionari di ingresso',endpoint='doc1',category='Documenti'))
adm.add_view(QuestionarioFollowupAdmin(Questionario_followup,name='Follow-up',endpoint='doc2',category='Documenti'))
adm.add_view(ModuloAdmin(Modulo_CDP,name='Moduli CDP',endpoint='doc3',category='Documenti'))
# endpoint='upload' -> l'archivio file risponde su /admin/upload/ (prima era
# /admin/myfileadmin/, un nome derivato dalla classe).
adm.add_view(MyFileAdmin(path, '/upload/', name='Archivio file', endpoint='upload', category='Documenti'))
adm.add_view(MyModelAdmin(User, dbsqla.session, name='Utenti', category='Sistema'))
adm.add_view(Logout())
