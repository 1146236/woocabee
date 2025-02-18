from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///words.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50), nullable=False)
    meaning = db.Column(db.String(255), nullable=False)
    example = db.Column(db.String(255), nullable=False)

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)  # Store user session ID or username
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)
    correct_answers = db.Column(db.Integer, default=0, nullable=False)  # Ensure default is 0
    wrong_answers = db.Column(db.Integer, default=0, nullable=False)  # Ensure default is 0
    status = db.Column(db.String(10), default="active")  # "active" or "learned"

    word = db.relationship('Word', backref=db.backref('progress', lazy=True))


def init_db():
    db.create_all()

if __name__ == "__main__":
    with app.app_context():
        init_db()
