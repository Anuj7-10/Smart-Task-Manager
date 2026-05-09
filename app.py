from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from analytics import get_task_statistics
from flask_socketio import SocketIO, emit

app = Flask(__name__)


app.config['SECRET_KEY'] = 'make_up_a_secret_password_here'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/task_manager_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
socketio = SocketIO(app)




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False) 
    
    tasks = db.relationship('Task', backref='owner', lazy=True)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), nullable=False, default='Medium')
    status = db.Column(db.String(20), nullable=False, default='Pending')
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



@app.route('/register', methods=['GET', 'POST'])
def register():
    
    if request.method == 'POST':
        
        form_username = request.form['username']
        form_password = request.form['password']
        
        
        existing_user = User.query.filter_by(username=form_username).first()
        if existing_user:
            return "Error: That username is already taken! Go back and try another."
            
        
        hashed_password = generate_password_hash(form_password)
        
        
        new_user = User(username=form_username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return "Success! You are now registered."

    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form_username = request.form['username']
        form_password = request.form['password']
        
        
        user = User.query.filter_by(username=form_username).first()
        
        
        if user and check_password_hash(user.password, form_password):
            
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            return "Error: Incorrect username or password."
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    
    if 'user_id' not in session:
        return redirect(url_for('login'))

    
    if request.method == 'POST':
        task_title = request.form['title']
        task_desc = request.form['description']
        task_priority = request.form['priority']
        
        
        new_task = Task(
            title=task_title, 
            description=task_desc, 
            priority=task_priority, 
            user_id=session['user_id']
        )
        db.session.add(new_task)
        db.session.commit()

        
        socketio.emit('live_notification', {'message': f'New task added: {task_title}'})
        
        
        
        return redirect(url_for('dashboard'))

   
    user_tasks = Task.query.filter_by(user_id=session['user_id']).all()
    
    
    stats = get_task_statistics(user_tasks)
    
    
    return render_template('dashboard.html', tasks=user_tasks, stats=stats)

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    
    task_to_delete = Task.query.get_or_404(task_id)
    
   
    if task_to_delete.user_id == session.get('user_id'):
        db.session.delete(task_to_delete)
        db.session.commit()

        socketio.emit('task_deleted', {'id': task_id})
        
    
    return redirect(url_for('dashboard'))

@app.route('/update/<int:task_id>')
def update_task(task_id):
    
    task_to_update = Task.query.get_or_404(task_id)
    
    
    if task_to_update.user_id == session.get('user_id'):
        
        if task_to_update.status == 'Pending':
            task_to_update.status = 'Completed'
        else:
            task_to_update.status = 'Pending'
            
        db.session.commit()
        
    return redirect(url_for('dashboard'))

@app.route('/')
def home():
    
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
    
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
        
    socketio.run(app, debug=True)