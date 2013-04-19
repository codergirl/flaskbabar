import os
from flask import Flask
import datetime

from flask.ext.sqlalchemy import SQLAlchemy
from flask import request

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

@app.route('/')
def index_page():
    return 'index'

@app.route('/create_user')
def create_user():
    return request.args.get('username'), request.args.get('email')

class BabarUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<Name %r>' % self.name

