from flask import Flask, jsonify, request
from threading import Lock
import requests

app = Flask(__name__)

# Хранилище подписчиков (для хранения callback_url сервисов)
subscribers = {}
lock = Lock()

@app.route('/register', methods=['POST'])
def register():
    service_name = request.json.get('service_name')
    callback_url = request.json.get('callback_url')

    with lock:
        subscribers[service_name] = callback_url
        print(f"Service {service_name} registered at {callback_url}")

    return jsonify({'message': f'Service {service_name} registered'}), 201

@app.route('/publish', methods=['POST'])
def publish():
    message = request.json.get('message')
    results = {}

    with lock:
        for service_name, callback_url in subscribers.items():
            try:
                print(f"Sending message to {service_name} at {callback_url}")
                response = requests.post(callback_url, json={'message': message})
                results[service_name] = response.status_code
                print(f"Response from {service_name}: {response.status_code}")
            except Exception as e:
                results[service_name] = str(e)
                print(f"Error sending to {service_name}: {e}")

    return jsonify(results), 200

if __name__ == '__main__':
    app.run(port=6000)
