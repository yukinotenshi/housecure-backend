from datetime import timedelta
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, messaging

from model import *


cred = credentials.Certificate('firebase_cred.json')
fb_client = firebase_admin.initialize_app(cred)
app = Flask(__name__)


@app.before_request
def connect_db():
    if db.is_closed():
        db.connect()


@app.after_request
def close_db(res):
    if not db.is_closed():
        db.close()

    return res


@app.route('/')
def home():
    return 'Serving Housecure Backend'


@app.route('/notify/<key>', methods=['POST'])
def notify(key):
    device = Device.get_or_none(Device.device_id == key)
    if not device:
        return '0'

    fcm_key = device.user.fcm_key
    message = messaging.Message(
        notification=messaging.Notification(
            title='Intruder alert in {}'.format(device.room),
            body='Someone entered {} on {}'.format(device.room, datetime.now()),
        ),
        android=messaging.AndroidConfig(
            priority="high"
        ),
        token=fcm_key,
    )

    response = messaging.send(message)
    Log(device=device, user=device.user).save()
    print(response)
    return '1'


@app.route('/register', methods=['POST'])
def register():
    fcm_key = request.json.get('fcm_key')
    user_key = request.json.get('user_key')
    user = User.get_or_none(User.user_key == user_key)
    if user:
        return jsonify(user.to_dict())
    user = User(fcm_key=fcm_key, user_key=user_key)
    user.save()

    return jsonify(user.to_dict())


@app.route('/status')
def status():
    user_key = request.headers.get('Authorization')
    user = User.get_or_none(User.user_key == user_key)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if not list(user.logs):
        return jsonify({'safe': True})

    log = user.logs[-1]

    if log.created_at > (datetime.now() - timedelta(minutes=5)):
        return jsonify({'safe': False})

    return jsonify({'safe': True})


@app.route('/add', methods=['POST'])
def add_device():
    user_key = request.headers.get('Authorization')
    user = User.get_or_none(User.user_key == user_key)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    device_id = request.json.get('device_id')
    room = request.json.get('room')
    device = Device(device_id=device_id, room=room, user=user)
    device.save()

    return jsonify(device.to_dict())


@app.route('/devices')
def get_devices():
    user_key = request.headers.get('Authorization')
    user = User.get_or_none(User.user_key == user_key)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    devices = Device.select().where(Device.user == user)
    devices = [d.to_dict() for d in devices]

    return jsonify({"devices": devices})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
