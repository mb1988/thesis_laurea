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
adm = admin.Admin(app, 'ASL', index_view=MyAdminIndexView())
adm.add_view(CentroAdmin(Centro))
adm.add_view(MedicoAdmin(Medico))
adm.add_view(PazienteAdmin(Paziente))
adm.add_view(QuestionarioIngressoAdmin(Questionario_ingresso,name='Questionario_ingresso',endpoint='doc1',category='Documenti'))
adm.add_view(QuestionarioFollowupAdmin(Questionario_followup,name='Questionario_followup',endpoint='doc2',category='Documenti'))
adm.add_view(ModuloAdmin(Modulo_CDP,name='Modulo_CDP',endpoint='doc3',category='Documenti'))
adm.add_view(MyFileAdmin(path, '/upload/', name='Upload'))
adm.add_view(MyModelAdmin(User, dbsqla.session))
adm.add_view(Logout())
