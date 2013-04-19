import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'index'
    

@app.route('/create_user/<username>')
def create_user(username):
    return 'User %s' % username



    
