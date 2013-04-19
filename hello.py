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
    due_date = db.Column(db.DateTime, nullable=True)
    active = db.Column(db.Boolean, default=True)


@app.route('/')
def index_page():
    return 'index'

@app.route('/create_user')
def create_user():
    new_user = BabarUser(request.args.get('username'), request.args.get('email'))
    db.session.add(new_user)
    db.session.commit()
    json = {new_user.id: {'username':new_user.name, 'email':new_user.email}}
    return jsonify(json)


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
    due_date = request.args.get('due_date')
    if due_date is not None:
        due_date = datetime.fromtimestamp(due_date)
    new_task = Task(user_id=the_user.id, name=task_name, description=task_description, dismissable=dismissable, due_date=due_date, active=True)
    db.session.add(new_task)
    db.session.commit()
    json = {new_task.id: get_task_view(new_task)}
    return jsonify(json)

@app.route('/dismiss_task')
def dismiss_task():
    the_user = db.session.query(BabarUser).filter_by(id=request.args.get('user_id')).first() 
    the_task = db.session.query(Task).filter_by(id=request.args.get('task_id')).first() 
    the_task.active = False
    db.session.commit()
    return jsonify(get_task_view(the_task))

@app.route('/get_tasks_for_user')
def get_tasks_for_user():
    the_user = db.session.query(BabarUser).filter_by(id=request.args.get('user_id')).first() 
    json = {}
    all_tasks = db.session.query(Task).filter_by(user_id=the_user.id)
    for task in all_tasks:
        json[task.id] = get_task_view(task)
    return jsonify(json)

def get_task_view(task):
    return {'name': task.name, 'description': task.description, 'dismissable': task.dismissable, 'due_date':task.due_date, 'active':task.active}

