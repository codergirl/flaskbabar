import os
from flask import Flask
import datetime

from flask.ext.sqlalchemy import SQLAlchemy
from flask import request, jsonify

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

class BabarUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<Name %r>' % self.name


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(128))
    description = db.Column(db.String(1024), nullable=True)
    dismissable = db.Column(db.Boolean, default=True)


@app.route('/')
def index_page():
    return 'index'

@app.route('/create_user')
def create_user():
    new_user = BabarUser(request.args.get('username'), request.args.get('email'))
    db.session.add(new_user)
    db.session.commit()
    return "User created: %s, %s" % (request.args.get('username'), request.args.get('email'))


@app.route('/get_users')
def get_users():
    all_users = BabarUser.query.all()
    json = {}
    for user in all_users:
        json[user.id] = {'name': user.name, 'email': user.email}
    return jsonify(json)

@app.route('/add_task')
def add_task():
    the_user = db.session.query(BabarUser).filter_by(id=request.args.get('user_id')).first() 
    task_name = request.args.get('name')
    task_description = request.args.get('description')
    dismissable = request.args.get('dismissable')
    if dismissable is None:
        dismissable = True
    new_task = Task(user_id=the_user.id, name=task_name, description=task_description, dismissable=dismissable)
    db.session.add(new_task)
    db.session.commit()

@app.route('/get_tasks_for_user')
def get_tasks_for_user():
    the_user = db.session.query(BabarUser).filter_by(id=request.args.get('user_id')).first() 
    json = {}
    all_tasks = db.session.query(Task).filter_by(user_id=the_user.id)
    for task in all_tasks:
        json[task.id] = {'name': task.name, 'description': task.description, 'dismissable': task.dismissable}  
    return jsonify(json)



