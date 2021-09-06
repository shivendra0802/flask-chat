from flask import Flask, render_template, url_for, request, redirect 
import os 
import time 
import json 
import pymongo 
from flask_socketio import SocketIO, join_room
from flask_login import current_user, login_user, login_required, logout_user, LoginManager
from db import get_user, save_user
from pymongo.errors import DuplicateKeyError





app = Flask(__name__)
app.secret_key = 'shivendra'
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            save_user(username, email, password)
            return redirect(url_for('login'))
        # except DuplicateKeyError:
        except pymongo.errors.DuplicateKeyError:
            message = "User already exists!"
    return render_template('signup.html', message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')
        user = get_user(username)

        if user and user.check_password(password_input):
            login_user(user)
            return redirect(url_for('home'))
        else:
            message = 'Failed to login!'
    return render_template('login.html', message=message)



@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')

    if username and room:
        return render_template('chat.html', username=username, room=room)
    else:
        return redirect(url_for('home'))        



@socketio.on('send_message')
def handel_send_message_event(data):
    app.logger.info("{} has sent the message to the room {}: {}".format(data['username'],
     data['room'], data['message']))
    socketio.emit('receive_message', data, room=data['room'])


@socketio.on('join_room')
def handel_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announsment', data)

@login_manager.user_loader
def load_user(username):
    return get_user(username)


if __name__ == "__main__":
    socketio.run(app, debug=True)    