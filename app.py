from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))

# Initialize database
@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    try:
        users = User.query.all()
        return render_template('index.html', users=users)
    except Exception as e:
        return f"Error loading users: {str(e)}", 500

@app.route('/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already exists!', 'error')
                return redirect(url_for('add_user'))
            
            new_user = User(name=name, email=email, phone=phone)
            db.session.add(new_user)
            db.session.commit()
            
            flash('User added successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error adding user: {str(e)}', 'error')
            return redirect(url_for('add_user'))
    
    return render_template('add_user.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    try:
        user = User.query.get_or_404(id)
    except:
        flash('User not found!', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            user.name = request.form['name']
            user.email = request.form['email']
            user.phone = request.form['phone']
            
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error updating user: {str(e)}', 'error')
    
    return render_template('edit_user.html', user=user)

@app.route('/delete/<int:id>')
def delete_user(id):
    try:
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/health')
def health_check():
    return 'OK', 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=False)
