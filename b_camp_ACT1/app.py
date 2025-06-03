from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# User model definition
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200))


@app.route('/')
def home():
    return redirect('/login')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        birthday = request.form['birthday']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']
        image = request.files['image']

        filename = secure_filename(image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists. Please use a different one."

        new_user = User(
            name=name,
            birthday=birthday,
            address=address,
            username=username,
            password=password,
            image=filepath
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect('/profile')
        else:
            error = "Incorrect username or password."
            return render_template('login.html', error=error)

    return render_template('login.html', error=None)

# Profile route
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')

    user = User.query.get(session['user_id'])
    if not user:
        return redirect('/login')

    birth_year = int(user.birthday.split("-")[0])
    current_year = datetime.now().year
    age = current_year - birth_year

    return render_template('profile.html', name=user.name, age=age, address=user.address, image=user.image)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
