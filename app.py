from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Database connection
try:
    from auth_db import Database
    db = Database()
    print("Database connection established and tables verified")
except Exception as e:
    print(f"Failed to initialize database: {e}")
    db = None

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        if db is None:
            flash('Database connection error', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if db is None:
            flash('Database connection failed', 'error')
            return redirect(url_for('login'))
            
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_id = db.authenticate_user(email, password)
        if user_id:
            session['user_id'] = user_id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if db is None:
            flash('Database connection failed', 'error')
            return redirect(url_for('register'))
            
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([first_name, last_name, email, password, confirm_password]):
            flash('All fields are required', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
        elif password != confirm_password:
            flash('Passwords do not match', 'error')
        else:
            if db.register_user(first_name, last_name, email, password):
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Email already exists', 'error')
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    db.cursor.execute("SELECT first_name, last_name, email FROM users WHERE id = %s", (user_id,))
    user_data = db.cursor.fetchone()
    
    if user_data:
        user = {
            'first_name': user_data[0],
            'last_name': user_data[1],
            'email': user_data[2]
        }
        return render_template('dashboard.html', user=user)
    else:
        flash('User not found', 'error')
        return redirect(url_for('logout'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)