from flask import Flask, render_template, redirect, request, session, flash, get_flashed_messages
from sqlalchemy.sql import func
from config import db, bcrypt

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(
        db.DateTime, server_default=func.now(), onupdate=func.now())

    @classmethod
    def add_new_user(cls, user_data):
        hashed_password = bcrypt.generate_password_hash(user_data['password'])
        new_user = cls(first_name=user_data['first_name'], last_name=user_data['last_name'],
                       email=user_data['email'], password=hashed_password)
        db.session.add(new_user)
        print("adding new user...")
        print(new_user)
        db.session.commit()
        return new_user

    @classmethod
    def validate_user(cls, user_data):
        is_valid = True
        # search for any existing users
        found_user = User.query.filter_by(email=user_data['email']).all()
        if found_user:
            is_valid = False
            flash("User already exists.")
        if len(user_data["first_name"]) < 1:
            is_valid = False
            flash("Please provide a first name", "reg_error")
        if len(user_data["last_name"]) < 1:
            is_valid = False
            flash("Please provide a last name", "reg_error")
        # if not EMAIL_REGEX.match(user_data["email"]):
        #     is_valid = False
        #     flash("Please provide a valid email", "reg_error")
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
    author_id = db.Column(db.Integer, db.ForeignKey(
        "users.id", ondelete="cascade"), nullable=False)
    author = db.relationship('User', foreign_keys=[
                             author_id], backref="user_entries")
    entry_time = db.Column(db.String)
    consump_date = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(
        db.DateTime, server_default=func.now(), onupdate=func.now())

    @classmethod
    def add_new_entry(cls, entry_data):
        new_entry = cls(amount=entry_data['quantity'], author_id=session['user_id'],
                        consump_date=entry_data['consump_date'], entry_time=entry_data['time'])
        db.session.add(new_entry)
        db.session.commit()
        return new_entry

    def get_time(self):
        xtime = self.created_at
        time = xtime.strftime("%I:%M %p")
        return time