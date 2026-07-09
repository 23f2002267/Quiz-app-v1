from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from sqlalchemy import text


db = SQLAlchemy()

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    fullname = db.Column(db.String(255), nullable=False)
    qualification = db.Column(db.String(255), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)  # Required for Flask-Login

    def __repr__(self):
        return f'<User {self.username}>'


class Subject(db.Model):
    __tablename__='subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    chapters = db.relationship('Chapter', backref='subject', cascade='all, delete-orphan')

class Chapter(db.Model):
    __tablename__='chapter'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id' ), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, unique=True)
    quizzes = db.relationship('Quiz', backref='chapter', cascade='all, delete-orphan')
    question = db.relationship('Question', backref='chapter', cascade='all, delete-orphan')

class Quiz(db.Model):
    __tablename__='quiz'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id' ), nullable=False)
    time_duration = db.Column(db.Time, nullable=False)
    questions = db.Column(db.Text, unique=True)
    remarks = db.Column(db.Text)

class Question(db.Model):
    __tablename__='question'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id' ), nullable=False)
    q_statement = db.Column(db.Text, nullable=False, unique=True)
    options = db.Column(db.JSON, nullable=False)
    correct_option = db.Column(db.String(255), nullable=False)

class Score(db.Model):
    __tablename__='score'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='CASCADE', onupdate='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'))
    timestamp_of_attempt = db.Column(db.DateTime, default=db.func.current_timestamp())
    total_score = db.Column(db.Float, nullable=False)
