import os
from flask import Flask
import datetime

from pymongo import MongoClient
client = MongoClient()

app = Flask(__name__)

@app.route('/')
def hello():
    return 'index'
    
@app.route('/show_users')
def show_users():
    connection = Connection()
    db = connection.babardb
    return db.users

@app.route('/create_user/<username>')
def create_user(username):
    print username
    # Get your DB
    db = client.babardb

    #_add_user(username)
    return 'User %s added' % username

def _add_user(username):
    db = client.babardb
    # Get your collection
    users = db.users

    # Create some objects
    user = {"username": username,
            "create_date": datetime.datetime.utcnow()}
    # Insert it
    users.insert(user)
    return True

    
