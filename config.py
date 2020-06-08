from flask import Flask, render_template, redirect, request, session, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import re
from datetime import date, datetime, time

app = Flask(__name__)
app.secret_key = "akdsjf534534yrgfgjlk"
bcrypt = Bcrypt(app)
# EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///water_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = './static/images/uploads'

db = SQLAlchemy(app)
migrate = Migrate(app, db)