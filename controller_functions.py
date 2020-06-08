from flask import Flask, render_template, redirect, request, session, flash, get_flashed_messages
from datetime import date, datetime, time
from config import db, bcrypt
import re
from models import User, Entry


def index():
    if 'user_id' in session:
        return redirect('/home')
    return render_template("index.html")


def register_new_user():
    validation_check = User.validate_user(request.form)
    if not validation_check:
        flash("User already exists.")
        return redirect("/")
    else:
        new_user = User.add_new_user(request.form)
        session["logged_in"] = True
        session["user_id"] = new_user.id
        return redirect("/home")


def username():
    found = False
    found_user = User.query.filter_by(email=request.form['email']).all()
    if found_user:
        found = True
    return render_template('/partials/username.html', found=found)


def login_page():
    return render_template("login_page.html")


def validate_login():
    user = User.query.filter_by(email=request.form['lemail']).all()
    print(user)
    is_valid = True if len(user) == 1 and bcrypt.check_password_hash(
        user[0].password, request.form['lpassword']) else False
    print(is_valid)
    if is_valid:
        session["logged_in"] = True
        session["user_id"] = user[0].id
        return redirect("/home")
    else:
        flash("Invalid Login Credentials", "log_error")
        return redirect("/login_page")


def success():
    if 'user_id' not in session:
        return redirect("/")
    else:
        user = User.query.get(session['user_id'])
        all_entries_by_user = Entry.query.filter_by(
            author_id=session['user_id']).order_by(Entry.consump_date.desc()).all()

        # # set the date var to the current full datetime
        date = datetime.now()
        # convert the date obj to a string holding only the day value
        date_str = date.strftime("%Y-%m-%d")
        print(date_str)

        consumption = Entry.query.filter_by(
            author_id=session['user_id']).filter_by(consump_date=date_str).all()

        print(consumption)

        today_consumption = 0
        for entry in consumption:
            today_consumption += entry.amount

        if today_consumption >= 64:
            flash("You hit your hydration goal of 64 oz!", "success")

        return render_template("home.html", user=user, entries=all_entries_by_user, consumption=today_consumption)


def add_entry():
    if 'user_id' not in session:
        return redirect("/")
    else:
        Entry.add_new_entry(request.form)
        flash("Successfully logged hydration.", "log_success")
        return redirect('/home')


def logout():
    session.clear()
    return redirect("/")


def edit_landing():
    if 'logged_in' not in session:
        flash("You must be logged in to complete that action.", "log_error")
        return redirect('/')
    user = User.query.filter_by(id=session['user_id'])
    return render_template('edit_prof.html', user=user[0])


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