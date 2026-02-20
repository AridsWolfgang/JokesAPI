from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Joke
from forms import LoginForm, RegistrationForm, JokeForm, EditProfileForm
import random
import os

app = Flask(__name__)
# Better secret key handling
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jokes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables and add default data
with app.app_context():
    db.create_all()
    
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@jokeapp.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")
    
    # Add some default jokes if none exist
    if Joke.query.count() == 0:
        default_jokes = [
            {"text": "Why do programmers prefer dark mode? Because light attracts bugs!", "category": "programming"},
            {"text": "Why don't eggs tell jokes? They'd crack each other up!", "category": "dad"},
            {"text": "I used to be a baker, but I couldn't make enough dough.", "category": "punny"},
            {"text": "Knock knock. Who's there? Lettuce. Lettuce who? Lettuce in, it's cold out here!", "category": "knock-knock"},
            {"text": "Why don't skeletons fight each other? They don't have the guts!", "category": "general"},
        ]
        
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            for joke_data in default_jokes:
                joke = Joke(
                    joke_text=joke_data["text"],  # Fixed: was 'text' but model expects 'joke_text'
                    category=joke_data["category"],
                    user_id=admin_user.id
                )
                db.session.add(joke)
            db.session.commit()
            print(f"Added {len(default_jokes)} default jokes!")

# Web Routes
@app.route('/')
def index():
    # Get some random jokes for the homepage
    jokes = Joke.query.order_by(db.func.random()).limit(5).all()
    categories = db.session.query(Joke.category, db.func.count(Joke.id)).group_by(Joke.category).all()
    return render_template('index.html', jokes=jokes, categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Fixed: No need for complex password handling
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_jokes = Joke.query.filter_by(user_id=current_user.id).order_by(Joke.created_at.desc()).all()
    total_likes = sum(joke.likes for joke in user_jokes)
    return render_template('dashboard.html', jokes=user_jokes, total_likes=total_likes)

@app.route('/add-joke', methods=['GET', 'POST'])
@login_required
def add_joke():
    form = JokeForm()
    if form.validate_on_submit():
        joke = Joke(
            joke_text=form.joke_text.data,
            category=form.category.data,
            user_id=current_user.id
        )
        db.session.add(joke)
        db.session.commit()
        flash('Your joke has been added! 🎭', 'success')
        return redirect(url_for('my_jokes'))
    
    return render_template('add_joke.html', form=form)

@app.route('/my-jokes')
@login_required
def my_jokes():
    page = request.args.get('page', 1, type=int)
    jokes = Joke.query.filter_by(user_id=current_user.id)\
                     .order_by(Joke.created_at.desc())\
                     .paginate(page=page, per_page=10, error_out=False)
    return render_template('my_jokes.html', jokes=jokes)

@app.route('/joke/<int:joke_id>/delete', methods=['POST'])
@login_required
def delete_joke(joke_id):
    joke = Joke.query.get_or_404(joke_id)
    
    # Check if user owns this joke or is admin
    if joke.user_id != current_user.id and not current_user.is_admin:
        flash('You cannot delete this joke.', 'danger')
        return redirect(url_for('index'))
    
    db.session.delete(joke)
    db.session.commit()
    flash('Joke deleted successfully.', 'success')
    return redirect(url_for('my_jokes'))

@app.route('/joke/<int:joke_id>/like', methods=['POST'])
@login_required
def like_joke(joke_id):
    joke = Joke.query.get_or_404(joke_id)
    joke.likes += 1
    db.session.commit()
    flash('You liked this joke! 👍', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    # Pre-populate form with current email
    form.email.data = current_user.email
    return render_template('profile.html', form=form)

@app.route('/browse')
def browse_jokes():
    category = request.args.get('category')
    page = request.args.get('page', 1, type=int)
    
    query = Joke.query
    if category:
        query = query.filter_by(category=category)
    
    jokes = query.order_by(Joke.created_at.desc()).paginate(page=page, per_page=12, error_out=False)
    categories = db.session.query(Joke.category, db.func.count(Joke.id)).group_by(Joke.category).all()
    
    return render_template('browse.html', jokes=jokes, categories=categories, current_category=category)

# API Routes (keeping your API functionality)
@app.route('/api/joke')
def api_random_joke():
    category = request.args.get('category')
    
    if category:
        jokes = Joke.query.filter_by(category=category).all()
    else:
        jokes = Joke.query.all()
    
    if not jokes:
        return jsonify({"error": "No jokes found"}), 404
    
    joke = random.choice(jokes)
    return jsonify(joke.to_dict())

@app.route('/api/jokes', methods=['GET'])
def api_get_jokes():
    category = request.args.get('category')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Joke.query
    if category:
        query = query.filter_by(category=category)
    
    jokes = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "total": jokes.total,
        "page": page,
        "per_page": per_page,
        "jokes": [joke.to_dict() for joke in jokes.items]
    })

@app.route('/api/jokes', methods=['POST'])
def api_add_joke():
    data = request.get_json()
    
    if not data or 'joke' not in data or 'category' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    # For API, assign to admin user if no auth (you might want to add API key auth later)
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        return jsonify({"error": "Admin user not found"}), 500
    
    joke = Joke(
        joke_text=data['joke'],
        category=data['category'],
        user_id=admin_user.id
    )
    
    db.session.add(joke)
    db.session.commit()
    
    return jsonify(joke.to_dict()), 201

if __name__ == '__main__':
    app.run(debug=True, port=3000)