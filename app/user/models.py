#tabella utenti che possono accedere all'applicazione

from app import dbsqla

class User(dbsqla.Model):
    id = dbsqla.Column(dbsqla.Integer, primary_key=True)
    username = dbsqla.Column(dbsqla.String(80), unique=True)
    email = dbsqla.Column(dbsqla.String(120))
    password = dbsqla.Column(dbsqla.String(64))
    admin = dbsqla.Column(dbsqla.Boolean())
    
    def is_authenticated(self):
        return True

    def is_active(self):
    	return True
	
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.login

