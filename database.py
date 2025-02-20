from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///words.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50), nullable=False)
    meaning = db.Column(db.String(255), nullable=False)
    example = db.Column(db.String(255), nullable=False)
    az = db.Column(db.String(255), nullable=False)
    ru = db.Column(db.String(255), nullable=False)
    tr = db.Column(db.String(255), nullable=False)

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link progress to user
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)
    correct_answers = db.Column(db.Integer, default=0, nullable=False)
    wrong_answers = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.String(10), default="active")  # "active" or "learned"

    word = db.relationship('Word', backref=db.backref('progress', lazy=True))
    user = db.relationship('User', backref=db.backref('progress', lazy=True))


def init_db():
    db.create_all()

if __name__ == "__main__":
    with app.app_context():
        init_db()
