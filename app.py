from flask import Flask
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from models import db, User
from controllers.auth import auth
from controllers.admin import admin
from controllers.user import user
from datetime import date, timedelta

today = date.today()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizmaster.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(id):
    print(User.query.get(id))
    return User.query.get(id)

def create_admin():
    with app.app_context():
        admin = User.query.filter_by(username='admin@quiz.com').first()
        if not admin:
            admin = User(
                username='admin@quiz.com',
                password_hash=generate_password_hash('pass'),
                fullname='QuizMaster',
                qualification='admin',
                dob=today,
                is_admin=True,
                is_active=True
                )
            
            db.session.add(admin)
            db.session.commit() 

app.register_blueprint(auth)
app.register_blueprint(user)
app.register_blueprint(admin)

if __name__ == '__main__':
    create_admin()
    app.run(debug=True)