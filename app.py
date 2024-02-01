from flask import Flask, render_template, request, redirect, flash, session, url_for,jsonify
from flask_bootstrap import Bootstrap
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # SQLite database file, you can change this to another database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = b'_5#y2L"F4Q8z\n\xec]/'


db = SQLAlchemy(app)
Bootstrap(app)

class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(50), unique=True, nullable=False)
        password = db.Column(db.String(60), nullable=False)
        is_authenticated = db.Column(db.Integer)
        
        
# GameScore model for storing game scores
class GameScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_name = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
        


# Decorator to check if the user is logged in
def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'error')
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapper

@login_required
def load_user(user_id):
    return User.query.all()

@login_required
def load_scores():
    return GameScore.query.all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contactus')
def contactus():
    return render_template('contactus.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Query all users from the database
        all_users = User.query.all()
        users = {str(user.id): user for user in all_users}
        user = next((user for user in users.values() if user.username == username and user.password == password), None)

        if user:
            user.is_authenticated = True
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    user_id = session.pop('user_id', None)
    if user_id:
        # Query the user from the database
        user = User.query.get(int(user_id))
        if user:
            user.is_authenticated = False
    flash('Logout successful', 'success')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Query all users from the database
        all_users = User.query.all()
        users = {str(user.id): user for user in all_users}
        # Check if the username is already taken
        if any(user.username == username for user in users.values()):
            flash('Username is already taken. Please choose another.', 'error')
        else:

            # Create a new user ID 
            new_user_id = str(len(users) + 1)
            # Create a new user
            new_user = User(id=new_user_id, username=username, password=password,is_authenticated=1)
            users[new_user_id] = new_user
            # save user in the database
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. You can now login.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/games')
def games():
    return render_template('games.html')

@app.route('/password_strength_checker')
@login_required
def password_strength_checker():
    return render_template('password_strength_checker.html')

@app.route('/cyber_security_quiz')
@login_required
def cyber_security_quiz():
    quizInstructions = """Welcome to the Cybersecurity Awareness Quiz!
    Instructions:\n
            1. This quiz contains a total of 24 questions.
            2. Choose the correct option for each question.
            3. Click the 'Submit Answer' button
            4. Good luck and stay cyber-aware!
            5. At the end to see your score."""
    return render_template('cyber_security_quiz.html', quizInstructions=quizInstructions)

@app.route('/security_threat_match')
@login_required
def security_threat_match():
    # List of cybersecurity threats
    threats = ['Phishing', 'Ransomware', 'Malware', 'Social Engineering']

    # List of corresponding descriptions (shuffled)
    descriptions = random.sample([
        'Attempts to trick individuals into revealing sensitive information.',
        'Encrypts files and demands a ransom for their release.',
        'Software designed to harm or exploit computer systems.',
        'Manipulates individuals to disclose confidential information.'
    ], len(threats))

    return render_template('security_threat_match.html', threats=threats, descriptions=descriptions)

@login_required
@app.route('/save_score', methods=['POST'])
def save_score():
    try:
        score_data = request.get_json()
        # ... validate and save score_data to the database
        new_score = GameScore(user_id=session['user_id'],game_name=score_data['game_name'],score=score_data['score'])
        db.session.add(new_score)
        db.session.commit() 
        return jsonify({'message': 'Score saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@login_required
@app.route('/game_scores')
def game_scores():
    game_scores = GameScore.query.filter_by(user_id=session['user_id']).all()
    return render_template('game_scores.html', game_scores=game_scores)

@login_required
@app.route('/delete_score/<int:id>', methods=['POST'])
def delete_score(id):
    # Delete the game score from the database
    score_to_delete = GameScore.query.get(id)
    db.session.delete(score_to_delete)
    db.session.commit()
    return redirect(url_for('game_scores'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)