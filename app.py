from flask import Flask, render_template, redirect, request, session, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate 
from sqlalchemy.sql import func 
from flask_bcrypt import Bcrypt
import re
import datetime

app = Flask(__name__)
app.secret_key="akdsjf534534yrgfgjlk"
bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///water_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    @classmethod
    def add_new_user(cls, user_data):
        hashed_password = bcrypt.generate_password_hash(user_data['password'])
        new_user = cls(first_name=user_data['first_name'], last_name=user_data['last_name'], email=user_data['email'], password=hashed_password)
        db.session.add(new_user)
        print("adding new user...")
        print(new_user)
        db.session.commit()
        return new_user
    
    @classmethod
    def validate_user(cls, user_data):
        is_valid = True
        if len(user_data["first_name"]) < 1:
            is_valid = False
            flash("Please provide a first name", "reg_error")
        if len(user_data["last_name"]) < 1:
            is_valid = False
            flash("Please provide a last name", "reg_error")
        if not EMAIL_REGEX.match(user_data["email"]):
            is_valid = False
            flash("Please provide a valid email", "reg_error" )
        if len(user_data["password"]) < 8:
            is_valid = False
            flash("Password should be at least 8 characters", "reg_error")
        if user_data["password"] != user_data["cpassword"]:
            is_valid = False
            flash("Passwords do not match", "reg_error")
        return is_valid

class Entry(db.Model):
    __tablename__ = "entries"
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"), nullable=False)
    author = db.relationship('User', foreign_keys=[author_id], backref="user_entries")
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    @classmethod
    def add_new_entry(cls, entry_data):
        new_entry = cls(amount=entry_data['quantity'], author_id=session['user_id'])
        db.session.add(new_entry)
        db.session.commit()
        return new_entry

    def get_time(self):
        xtime = self.created_at
        time = xtime.strftime("%I:%M %p")
        return time

    def get_date(self):
        xdate = self.created_at
        date = xdate.strftime("%x")
        return date

@app.route('/')
def index():
    return render_template("login_reg.html")

@app.route('/register', methods=["POST"])
def register_new_user():
    validation_check = User.validate_user(request.form)
    if not validation_check:
        return redirect("/")
    else:
        new_user = User.add_new_user(request.form)
        session["user_id"] = new_user.id
        return redirect("/home")

@app.route('/login', methods=["POST"])
def validate_login():
    user = User.query.filter_by(email=request.form['lemail']).all()
    is_valid = True if len(user)==1 and bcrypt.check_password_hash(user[0].password, request.form['lpassword']) else False
    if is_valid:
        session["logged_in"] = True
        session["user_id"] = user[0].id
        return redirect("/home")
    else:
        flash("Invalid Login Credentials", "log_error")
        return redirect("/")

@app.route('/home')
def success():
    if 'user_id' not in session:
        return redirect("/")
    else:
        user = User.query.get(session['user_id'])
        all_entries_by_user = Entry.query.filter_by(author_id=session['user_id']).order_by(Entry.created_at.desc()).all()

        # set to query of users (today's consumption)
        current_consumption = 20

        return render_template("home.html", user=user, entries=all_entries_by_user, consumption=current_consumption)

@app.route('/add_entry', methods=["POST"])
def add_entry():
    if 'user_id' not in session:
        return redirect("/")
    else:
        Entry.add_new_entry(request.form)
        flash("Successfully logged hydration. Congrats on staying healthy!")
        return redirect('/home')

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

@app.route('/edit_profile')
def edit_landing():
    if 'logged_in' not in session:
        flash("You must be logged in to complete that action.", "log_error")
        return redirect('/')
    user = User.query.filter_by(id=session['user_id'])
    return render_template('edit_prof.html', user=user[0])

@app.route('/update_user', methods=["POST"])
def update_prof():
    if 'logged_in' not in session:
        flash("You must be logged in to complete that action.", "log_error")
        return redirect('/')
    
    else:
        user = User.query.get(session['user_id'])
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.email = request.form['email']
        print(user.first_name, user.last_name, user.email)
        db.session.commit()

        return redirect('/edit_profile')

if __name__  == "__main__":
    app.run(debug=True)