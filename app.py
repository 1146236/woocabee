from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from database import db, Word, UserProgress, app, User, bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import random

app.secret_key = "supersecretkey"  # Used for user sessions 


@app.route('/')
def index():
    return render_template('index.html')

# Ensure login manager is set up after app is created
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirects to login page if user is not authenticated

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Load user from database

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'})
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return jsonify({'message': 'Login successful'})
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/get-word')
@login_required
def get_word():
    # Retrieve words marked as "learned" by the current user
    learned_word_ids = db.session.query(UserProgress.word_id).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.status == "learned"
    ).all()

    # Convert list of tuples to a simple list
    learned_word_ids = [word_id[0] for word_id in learned_word_ids]

    print(f"User ID: {current_user.id} - Learned Word IDs: {learned_word_ids}")  # Debugging

    # Fetch a random word that the user has not yet learned
    word = Word.query.filter(~Word.id.in_(learned_word_ids)).order_by(db.func.random()).first()

    if word:
        print(f"Fetching Word: {word.word} (ID: {word.id}) for User {current_user.id}")  # Debugging
        return jsonify({
            'word_id': word.id,
            'word': word.word,
            'meaning': word.meaning,
            'example': word.example,
            'az': getattr(word, 'az', "-"),
            'ru': getattr(word, 'ru', "-"),
            'tr': getattr(word, 'tr', "-")
        })

    print(f"No words available for User {current_user.id}")  # Debugging
    return jsonify({'error': 'No words available'})



@app.route('/submit-answer', methods=['POST'])
@login_required
def submit_answer():
    data = request.json
    word_id = data.get('word_id')
    user_answer = data.get('answer', "").strip().lower()

    word = db.session.get(Word, word_id)  # ✅ Use `db.session.get()` to avoid SQLAlchemy warning
    if not word:
        return jsonify({'error': 'Word not found'})

    # Retrieve existing progress or create a new one
    progress = UserProgress.query.filter_by(user_id=current_user.id, word_id=word_id).first()

    if not progress:
        progress = UserProgress(user_id=current_user.id, word_id=word_id, correct_answers=0, wrong_answers=0, status="active")
        db.session.add(progress)
        db.session.commit()

    # ✅ Ensure correct and wrong counts are never None
    progress.correct_answers = progress.correct_answers or 0
    progress.wrong_answers = progress.wrong_answers or 0

    if user_answer == word.word.lower():
        progress.correct_answers += 1
        if progress.correct_answers >= 5:
            progress.status = "learned"  # ✅ Mark word as "learned"
        db.session.commit()
        print(f"✅ Correct Answer! User {current_user.id} Progress: {progress.correct_answers}")  # Debugging
        return jsonify({'result': 'correct', 'correct_answers': progress.correct_answers})
    else:
        progress.wrong_answers += 1
        db.session.commit()
        print(f"❌ Wrong Answer! User {current_user.id} Progress: {progress.wrong_answers}")  # Debugging
        return jsonify({'result': 'wrong', 'wrong_answers': progress.wrong_answers, 'correct_answer': word.word})


        
@app.route('/user-stats')
@login_required
def user_stats():
    try:
        # ✅ Ensure progress values are summed correctly
        correct_total = db.session.query(db.func.sum(UserProgress.correct_answers)).filter(
            UserProgress.user_id == current_user.id).scalar() or 0

        wrong_total = db.session.query(db.func.sum(UserProgress.wrong_answers)).filter(
            UserProgress.user_id == current_user.id).scalar() or 0

        learned_count = db.session.query(UserProgress).filter(
            UserProgress.user_id == current_user.id, UserProgress.status == "learned").count()

        print(f"✅ User ID: {current_user.id} - Correct Total: {correct_total}, Wrong Total: {wrong_total}, Learned: {learned_count}")  # Debugging

        return jsonify({'correct': correct_total, 'wrong': wrong_total, 'learned': learned_count})

    except Exception as e:
        print(f"❌ Error in /user-stats: {str(e)}")  # Log errors
        return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
