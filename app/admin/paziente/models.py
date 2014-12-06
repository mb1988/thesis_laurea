from app import db
from app.admin.centro.models import Centro
from app.admin.medico.models import Medico


class Paziente(db.Document):
    cognome = db.StringField(max_length=50, required=True)
    nome = db.StringField(max_length=50, required=True)
    nascita = db.DateTimeField()
    medico = db.ReferenceField('Medico', dbref=True)# , dbref=False?
    centro = db.ReferenceField('Centro', dbref=True)# , dbref=False?
    
    def __unicode__(self):
		return '%s - %s' % (self.cognome, self.nome)

