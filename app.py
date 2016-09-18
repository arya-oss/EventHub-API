#!/usr/bin/env python

import os
import bcrypt
import re

from datetime import datetime, date

from flask import Flask, abort, request, json, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_httpauth import HTTPBasicAuth
from flask_migrate import Migrate

# initialization

app = Flask(__name__)

app.config['SECRET_KEY'] = 'somerandomstring'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# extensions

db = SQLAlchemy(app)
auth = HTTPBasicAuth()
migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = 'user'
    _id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    password = db.Column(db.String(64))
    first_name = db.Column(db.String(16))
    last_name = db.Column(db.String(16))
    email = db.Column(db.String(32), unique=True)
    phone = db.Column(db.String(13))
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=0)
    feedback = db.relationship('Feedback', backref='User', uselist=False)

    def __init__(self, username, first_name, email, last_name, phone):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
    
    def hash_password(self, password):
        self.password = bcrypt.hashpw(password, bcrypt.gensalt())

    def check_password(self, password):
        return bcrypt.checkpw(password, str(self.password))

    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def __str__(self):
        return '<User: %s>' % str(self.username)

class Feedback(db.Model):
    __tablename__='feedback'
    _id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer)
    comment = db.Column(db.String(50))
    ts_submit = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user._id'))

    def __init__(self, stars, comment):
        self.stars = stars
        self.comment = comment

    def __str__(self):
        return '<Feedback: %s>' % str(self.comment)

event_user = db.Table('event_user',
    db.Column('event_id', db.Integer, db.ForeignKey('event._id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user._id')),
    db.Column('interested', db.Boolean)
)

class Event(db.Model):
    __tablename__='event'
    _id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32))
    location = db.Column(db.String(32))
    schedule = db.Column(db.DateTime)
    logo_url = db.Column(db.String(128), default="assets/logo.png")
    requirements = db.Column(db.String(64))
    refreshment = db.Column(db.Boolean)
    contact = db.Column(db.String(13))
    contact_alt = db.Column(db.String(12))
    event_user = db.relationship(
        'User',
        secondary=event_user,
        backref=db.backref('events', lazy='dynamic')
    )

    def __init__(self, title, location, schedule, contact):
        self.title = title
        self.location= location
        self.schedule = schedule
        self.contact = contact

    def to_json(self):
        return {
            '_id' : self._id,
            'title': self.title, 
            'location': self.location, 
            'schedule': self.schedule, 
            'logo_url': self.logo_url, 
            'requirements': self.requirements,
            'contact' : self.contact,
            'contact_alt' : self.contact_alt,
            'going': len(self.event_user)
        }

    def __str__(self):
        return '<Event: %s>' % str(self.title)

def custom_error(status_code, err_msg):
    response = {
        'status': status_code,
        'message': err_msg
    }
    return jsonify(response)

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=str(username)).first()
    if not user or not user.check_password(str(password)):
        return False
    g.user = user
    return True

@app.route('/api/v1/users', methods=['POST'])
def new_user():
    username = str(request.json.get('username'))
    password = str(request.json.get('password'))
    first_name = str(request.json.get('first_name'))
    last_name = str(request.json.get('last_name'))
    email = str(request.json.get('email'))
    phone = str(request.json.get('phone'))
    
    if re.match(r"^[a-zA-Z0-9_]+$", username) is None:
        return custom_error(400, 'username format is lowercase and numeric')
    if first_name is None or len(first_name) < 3:
        return custom_error(400, 'first_name cannot be null')
    if re.match(r"[^@]+@[^@]+\.[^@]+", email) is None:
        return custom_error(400, 'email is not correct')
    if password is None or len(password) < 6:
        return custom_error(400, 'password length must be > 6')
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return custom_error(409, 'username already exists ! try differenr')
    
    user = User(username, first_name, email, last_name, phone)
    user.hash_password(password)

    # First user is always Admin
    u = User.query.all()
    if u is None or len(u) == 0:
        user.is_admin = True

    db.session.add(user)
    db.session.commit()

    return (jsonify({'username': user.username}), 201, {'Location': url_for('get_user', _id=user._id, _external=True)})

@app.route('/api/v1/users/<int:_id>', methods=['GET'])
def get_user(_id):
    user = User.query.get(_id)
    if not user:
        custom_error(404, 'User not found')
    return jsonify({'full_name': user.full_name(), 'email': user.email, 'phone': user.phone})

@app.route('/api/v1/users', methods=['GET'])
@auth.login_required
def get_all_user():
    users = User.query.all()
    if not users:
        return jsonify({'status':'success', 'count':0})
    else:
        res = {'status':'success', 'count': len(users), 'users': []}
        for user in users:
            res['users'].append({'_id': user._id,'full_name': user.full_name(), 'email': user.email, 'phone': user.phone})

        return jsonify(res)

@app.route('/api/v1/feedback', methods=['POST'])
@auth.login_required
def submit_feedback():
    stars = int(request.json.get('stars'))
    comment = str(request.json.get('comment'))
    f = Feedback.query.filter_by(user_id=g.user._id).first()
    if f is not None:
        return jsonify({'status':'error', 'message':'Feedback Already Submitted !'})

    feedback = Feedback(stars, comment)
    feedback.user_id = g.user._id
    db.session.add(feedback)
    db.session.commit()

    return jsonify({'status':'success', 'message':'Feedback Submitted !'})

@app.route('/api/v1/events/<int:_id>', methods=['GET'])
@auth.login_required
def get_event(_id):
    event = Event.query.get(_id)

    if event is None:
        return custom_error(404, 'Event not found')

    return jsonify({'status': 'success', 'event': event.to_json()})

@app.route('/api/v1/events', methods=['GET'])
@auth.login_required
def get_all_event():
    when = int(request.args.get('when'))
    if when == 0:
        events = Event.query.filter(func.date(Event.schedule) < date.today())
    elif when == 1:
        events = Event.query.filter(func.date(Event.schedule) == date.today())
    elif when == 2:
        events = Event.query.filter(func.date(Event.schedule) > date.today())
    else:
        return custom_error(400, 'Invalid query body')

    if events is None:
        return custom_error(404, 'Event not found')

    response = {'status': 'success', 'events': []}
    for event in events:
        response['events'].append(event.to_json())
    return jsonify(response)

@app.route('/api/v1/events', methods=['POST'])
@auth.login_required
def create_event():
    if g.user.is_admin == False:
        return custom_error(400, 'You are not an admin')
    title = str(request.json.get('title'))
    location = str(request.json.get('location'))
    schedule = datetime.strptime(str(request.json.get('schedule')), '%Y-%m-%d %H:%M:%S')
    logo_url = str(request.json.get('logo_url'))
    contact = str(request.json.get('contact'))
    contact_alt = str(request.json.get('contact_alt'))
    requirements = str(request.json.get('requirements'))
    refreshment = int(request.json.get('refreshment'))
    event = Event(title, location, schedule, contact)
    event.logo_url = logo_url
    event.contact_alt = contact_alt
    event.requirements = requirements
    event.refreshment = refreshment
    db.session.add(event)
    db.session.commit()

    return (jsonify({'title': event.title}), 201, {'Location': url_for('get_event', _id=event._id, _external=True)})

@app.route('/api/v1/admin/<int:_id>', methods=['PUT'])
@auth.login_required
def create_admin(_id):
    if g.user.is_admin is None or g.user.is_admin == False:
        return custom_error(400, 'You are not an admin')
    user = User.query.get(_id)
    if user is None:
        return custom_error(404, 'User not found')
    
    user.is_admin = True
    db.session.commit()
    print user.username, ' made admin by ', g.user.username
    return jsonify({"status":"success", "message":"new admin created"})

@app.route('/api/v1/join/<int:_id>', methods=['POST'])
@auth.login_required
def join_event(_id):
    event = Event.query.get(_id)
    if event is None:
        return custom_error(404, "Event not found !")
    event.event_user.append(g.user)
    db.session.commit()
    return jsonify({"status":"success", "message":"Successfully Joined"})

@app.route('/api/v1/going/<int:_id>', methods=['GET'])
@auth.login_required
def going_user(_id):
    event = Event.query.get(_id)
    if event is None:
        return custom_error(404, "Event not found !")
    response = {"status":"success", "count": len(event.event_user), "users": []}
    for user in event.event_user:
        response["users"].append(user.full_name())
    return jsonify(response)

if __name__=='__main__':
    if not os.path.exists('db.sqlite3'):
        db.create_all()

    app.run(debug=True)

