from flask import Flask, render_template, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy #pylint: disable=import-error
from flask_migrate import Migrate #pylint: disable=import-error
from sqlalchemy.sql import func #pylint: disable=import-error
from flask_bcrypt import Bcrypt
import re

app = Flask(__name__)
app.secret_key="akdsjf534534yrgfgjlk"
bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dojos_ninjas.db'
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
            flash("Please provide a first name", 'reg_error')
        if len(user_data["last_name"]) < 1:
            is_valid = False
            flash("Please provide a last name", 'reg_error')
        if not EMAIL_REGEX.match(user_data["email"]):
            is_valid = False
            flash("Please provide a valid email", 'reg_error')
        if len(user_data["password"]) < 8:
            is_valid = False
            flash("Password should be at least 8 characters", 'reg_error')
        if user_data["password"] != user_data["cpw"]:
            is_valid = False
            flash("Passwords do not match", 'reg_error')
        return is_valid

class Entry(db.Model):
    __tablename__ = "entries"
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"), nullable=False)
    author = db.relationship('User', foreign_keys=[author_id], backref="user_entries")
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    # @classmethod
    # def add_new_entry(cls, entry_data):
    #     new_entry = cls(amount=entry_data['selection'])

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
        



if __name__  == "__main__":
    app.run(debug=True)