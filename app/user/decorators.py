#crea i requisiti per inizializare flask-login

from flask.ext import login

from app import dbsqla,app
from app.user.models import User

# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.setup_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return dbsqla.session.query(User).get(user_id)
