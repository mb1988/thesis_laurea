from flask.ext.script import Manager

from app import dbsqla, app
from app.user.models import User

manager = Manager(app)

@manager.command
def setup():
	dbsqla.create_all()
	admin = User( username = 'admin', email = 'admin@gmail.com', password = 'password', admin = True )
	guest = User( username =' guest', email = 'guest@gmail.com', password = 'password', admin = False )
	dbsqla.session.add(admin)
	dbsqla.session.add(guest)
	dbsqla.session.commit()

if __name__ == "__main__":
    manager.run()
