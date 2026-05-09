from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from analytics import get_task_statistics
from flask_socketio import SocketIO, emit

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
app.config['SECRET_KEY'] = 'make_up_a_secret_password_here'
# Format: postgresql://username:password@localhost/database_name
# Replace 'your_password' with your actual pgAdmin password!
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/task_manager_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database tool
db = SQLAlchemy(app)
socketio = SocketIO(app)

# --- DATABASE MODELS (TABLES) ---

# 1. User Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False) # We will encrypt this later!
    # Link tasks to users (One User can have Many Tasks)
    tasks = db.relationship('Task', backref='owner', lazy=True)

# 2. Task Table (Matches assignment requirements)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), nullable=False, default='Medium')
    status = db.Column(db.String(20), nullable=False, default='Pending')
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    # This links the task to a specific user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# --- ROUTES ---
# --- ROUTES ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    # If the user clicked the "Register" button, it sends a POST request
    if request.method == 'POST':
        # Grab what they typed into the HTML form
        form_username = request.form['username']
        form_password = request.form['password']
        
        # Check if the username already exists in the database
        existing_user = User.query.filter_by(username=form_username).first()
        if existing_user:
            return "Error: That username is already taken! Go back and try another."
            
        # Encrypt the password so it's not saved as plain text
        hashed_password = generate_password_hash(form_password)
        
        # Create a new User object and save it to the database
        new_user = User(username=form_username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return "Success! You are now registered."

    # If it's just a GET request, show them the HTML page
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form_username = request.form['username']
        form_password = request.form['password']
        
        # Find the user in the database
        user = User.query.filter_by(username=form_username).first()
        
        # Check if user exists AND the password matches the hashed password
        if user and check_password_hash(user.password, form_password):
            # Give them a "wristband" by saving their ID in the session dictionary
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            return "Error: Incorrect username or password."
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Remove the user's wristband by clearing the session
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # SECURITY CHECK: If they don't have a wristband, kick them back to login
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # If they submitted the "Add Task" form
    if request.method == 'POST':
        task_title = request.form['title']
        task_desc = request.form['description']
        task_priority = request.form['priority']
        
        # Create the task and link it to the currently logged-in user
        new_task = Task(
            title=task_title, 
            description=task_desc, 
            priority=task_priority, 
            user_id=session['user_id']
        )
        db.session.add(new_task)
        db.session.commit()

        # --- NEW WEBSOCKET CODE ---
        # Broadcast the ACTUAL task details to all connected users
        # --- NEW WEBSOCKET CODE ---
        # Broadcast a message to all connected users
        socketio.emit('live_notification', {'message': f'New task added: {task_title}'})
        # --------------------------
        # --------------------------
        
        # Refresh the page to show the new task
        return redirect(url_for('dashboard'))

    # ... (keep the POST request stuff exactly the same) ...

    # If they are just viewing the page, fetch all tasks that belong to them
    user_tasks = Task.query.filter_by(user_id=session['user_id']).all()
    
    # NEW: Calculate our statistics using Pandas!
    stats = get_task_statistics(user_tasks)
    
    # Send BOTH the tasks and the stats to the HTML page
    return render_template('dashboard.html', tasks=user_tasks, stats=stats)

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    # Find the task by its ID
    task_to_delete = Task.query.get_or_404(task_id)
    
    # Security check: Make sure the logged-in user actually owns this task!
    if task_to_delete.user_id == session.get('user_id'):
        db.session.delete(task_to_delete)
        db.session.commit()

        socketio.emit('task_deleted', {'id': task_id})
        
    # Send them back to the dashboard
    return redirect(url_for('dashboard'))

@app.route('/update/<int:task_id>')
def update_task(task_id):
    # Find the task
    task_to_update = Task.query.get_or_404(task_id)
    
    # Security check
    if task_to_update.user_id == session.get('user_id'):
        # Toggle the status
        if task_to_update.status == 'Pending':
            task_to_update.status = 'Completed'
        else:
            task_to_update.status = 'Pending'
            
        db.session.commit()
        
    return redirect(url_for('dashboard'))

@app.route('/')
def home():
    # Check if the user has a wristband (user_id in session)
    if 'user_id' in session:
        return f"""
        <h1>Welcome back, {session['username']}!</h1>
        <p>Your VIP wristband is active.</p>
        <a href='/logout'>Logout</a>
        """
    else:
        return f"""
        <h1>Welcome to Smart Task Manager</h1>
        <p>Please log in to continue.</p>
        <a href='/login'>Login</a> | <a href='/register'>Register</a>
        """

if __name__ == '__main__':
    # This special command creates the tables in PostgreSQL before the server starts
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
        
    socketio.run(app, debug=True)