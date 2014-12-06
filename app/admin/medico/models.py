from app import db
from app.admin.centro.models import Centro

class Medico(db.Document):
    cognome = db.StringField(max_length=50, required=True)
    nome = db.StringField(max_length=50)
    centro = db.ReferenceField('Centro', dbref=True)# , dbref=False?
    
    def __unicode__(self):
		return '%s - %s' % (self.cognome, self.nome)

