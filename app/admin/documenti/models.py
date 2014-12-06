from app import db
from app.admin.paziente.models import Paziente

class Questionario_ingresso(db.DynamicDocument):
	paziente = db.ReferenceField('Paziente', dbref=True, required=True)# , dbref=False?

class Modulo_CDP(db.DynamicDocument):
	paziente = db.ReferenceField('Paziente', dbref=True, required=True)# , dbref=False?
	
class Questionario_followup(db.DynamicDocument):
	paziente = db.ReferenceField('Paziente', dbref=True, required=True)# , dbref=False?
