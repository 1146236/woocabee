from flask import Flask, render_template, jsonify, request, session
from database import db, Word, UserProgress, app
import random

app.secret_key = "supersecretkey"  # Used for user sessions v 1.1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-word')
def get_word():
    user_id = session.get('user_id', str(random.randint(1000, 9999)))  # Simulate a unique user
    session['user_id'] = user_id

    word = Word.query.filter(~Word.id.in_(
        db.session.query(UserProgress.word_id).filter(UserProgress.user_id == user_id, UserProgress.status == "learned")
    )).order_by(db.func.random()).first()

    if word:
        return jsonify({'word_id': word.id, 'word': word.word})
    return jsonify({'error': 'No words available'})

@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    data = request.json
    word_id = data.get('word_id')
    user_answer = data.get('answer').strip().lower()
    user_id = session.get('user_id', 'unknown')

    word = Word.query.get(word_id)
    if not word:
        return jsonify({'error': 'Word not found'})

    progress = UserProgress.query.filter_by(user_id=user_id, word_id=word_id).first()
    if not progress:
        progress = UserProgress(user_id=user_id, word_id=word_id)
        db.session.add(progress)

    if user_answer == word.meaning.lower():
        progress.correct_answers += 1
        if progress.correct_answers >= 5:
            progress.status = "learned"
        db.session.commit()
        return jsonify({'result': 'correct', 'correct_answers': progress.correct_answers})
    else:
        progress.wrong_answers += 1
        db.session.commit()
        return jsonify({'result': 'wrong', 'wrong_answers': progress.wrong_answers})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
