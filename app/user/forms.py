#classe login form per eseguire il login

from flask.ext import wtf

from app import dbsqla
from app.user.models import User

class LoginForm(wtf.Form):
    login = wtf.TextField(validators=[wtf.required()])
    password = wtf.PasswordField(validators=[wtf.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise wtf.ValidationError('Invalid user')

        if user.password != self.password.data:
            raise wtf.ValidationError('Invalid password')
        
    def get_user(self):
        return dbsqla.session.query(User).filter_by(username=self.login.data).first()



