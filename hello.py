import os
from flask import Flask
import datetime
import time

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
    due_date = db.Column(db.DateTime, nullable=True)
    active = db.Column(db.Boolean, default=True)


@app.route('/')
def index_page():
    return 'index'

@app.route('/create_user')  # required: username, email
def create_user():
    new_user = BabarUser(request.args.get('username'), request.args.get('email'))
    db.session.add(new_user)
    db.session.commit()
    json = {new_user.id: {'username':new_user.name, 'email':new_user.email}}
    return jsonify(json)


@app.route('/get_users') # none
def get_users():
    all_users = BabarUser.query.all()
    json = {}
    for user in all_users:
        json[user.id] = {'name': user.name, 'email': user.email}
    return jsonify(json)

@app.route('/add_task') # required: user_id, name. optional: description, dismissable (default true), due date (default none)
def add_task():
    the_user = db.session.query(BabarUser).filter_by(id=request.args.get('user_id')).first() 
    task_name = request.args.get('name')
    task_description = request.args.get('description')
    dismissable = request.args.get('dismissable')
    if dismissable is None:
        dismissable = True
    due_date = request.args.get('due_date')
    if due_date is not None:
        due_date = datetime.datetime.fromtimestamp(float(due_date))
    new_task = Task(user_id=the_user.id, name=task_name, description=task_description, dismissable=dismissable, due_date=due_date, active=True)
    db.session.add(new_task)
    db.session.commit()
    json = {new_task.id: get_task_view(new_task)}
    return jsonify(json)

@app.route('/dismiss_task') # required: user_id, task_id
def dismiss_task():
    the_user = db.session.query(BabarUser).filter_by(id=request.args.get('user_id')).first() 
    the_task = db.session.query(Task).filter_by(id=request.args.get('task_id')).first() 
    the_task.active = False
    db.session.commit()
    return get_tasks_for_user()

@app.route('/snooze_task') # required: user_id, task_id
def snooze_task():
    the_user = db.session.query(BabarUser).filter_by(id=request.args.get('user_id')).first() 
    the_task = db.session.query(Task).filter_by(id=request.args.get('task_id')).first() 
    if 'until' in request.args:
        due_date = datetime.datetime.fromtimestamp(float(request.args.get('until')))
    else:
        due_date = datetime.datetime.now() + datetime.timedelta(seconds=60*10)
    the_task.due_date = due_date
    db.session.commit()
    return get_tasks_for_user()

@app.route('/get_tasks_for_user') # required: user_id
def get_tasks_for_user():
    the_user = db.session.query(BabarUser).filter_by(id=request.args.get('user_id')).first() 
    json = {}
    all_tasks = db.session.query(Task).filter_by(user_id=the_user.id, active=True)
    for task in all_tasks:
        json[task.id] = get_task_view(task)
    return jsonify(json)

@app.route('/pass_task') # required: user_id, task_id, to_user_id
def pass_task():
    the_user = db.session.query(BabarUser).filter_by(id=request.args.get('user_id')).first() 
    the_task = db.session.query(Task).filter_by(id=request.args.get('task_id')).first() 
    to_user = db.session.query(BabarUser).filter_by(id=request.args.get('to_user_id')).first() 
    the_task.user_id = to_user.id
    db.session.commit()
    return get_tasks_for_user()

def get_task_view(task): 
    due_date = task.due_date
    if task.due_date is not None:
        due_date = time.mktime(due_date.timetuple())
    return {'name': task.name, 'description': task.description, 'dismissable': task.dismissable, 'due_date':due_date, 'active':task.active}

