from flask import Flask, jsonify, request, render_template
import json
import os
import requests
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

ORDERS_FILE = os.path.join(os.path.dirname(__file__), 'orders.json')


# Функция для загрузки заказов из файла
def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


# Функция для сохранения заказов в файл
def save_orders(orders):
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=4)


# Функция для отправки сообщений в шину данных (если нужно отправить изменения в другие сервисы)
def send_message_to_bus(message):
    try:
        response = requests.post("http://localhost:6000/publish", json={"message": message})
        if response.status_code == 200:
            print("Message sent to the bus successfully.")
        else:
            print(f"Failed to send message to the bus: {response.status_code}")
    except Exception as e:
        print(f"Error sending message to bus: {e}")


# Главная страница для теста
@app.route('/')
def index():
    return render_template('index.html')


# Получение всех заказов для юзер-сервиса
@app.route('/orders', methods=['GET'])
def get_orders():
    orders = load_orders()
    return jsonify({'orders': orders})


# Обновление статуса заказа (получение от юзер-сервиса)
@app.route('/order/response', methods=['POST'])
def update_order_status():
    if request.is_json:
        order_id = request.json.get('order_id')  # Получаем order_id из JSON
        status = request.json.get('status')      # Получаем новый статус из JSON
    else:
        return jsonify({'message': 'Invalid Content-Type, must be application/json'}), 415

    if not order_id or not status:
        return jsonify({'message': 'Invalid data provided'}), 400

    orders = load_orders()
    order = next((order for order in orders if order["id"] == order_id), None)

    if order:
        order["status"] = status
        save_orders(orders)

        # Отправляем обновление статуса заказа в шину данных
        message = f"Order ID {order_id} status updated to {status}"
        send_message_to_bus(message)

        return jsonify({'message': 'Order status updated successfully'}), 200
    else:
        return jsonify({'message': 'Order not found'}), 404


# Создание нового заказа
@app.route('/order', methods=['POST'])
def create_order():
    username = request.json.get('username')
    item_id = request.json.get('item_id')

    # Преобразуем item_id в число
    try:
        item_id = int(item_id)  # Преобразуем item_id в число
    except ValueError:
        return jsonify({'message': 'Item ID must be a number'}), 400

    if not username or not item_id:
        return jsonify({'message': 'Invalid data'}), 400

    orders = load_orders()

    # Генерация уникального идентификатора для каждого нового заказа (UUID)
    order_id = str(uuid.uuid4())  # Используем UUID для уникального идентификатора
    order = {'id': order_id, 'username': username, 'item_id': item_id, 'status': 'Pending'}
    
    orders.append(order)
    save_orders(orders)

    # Отправляем сообщение о новом заказе через шину данных
    message = f"New order created by {username}, item ID: {item_id}, status: Pending"
    send_message_to_bus(message)

    return jsonify({'message': 'Order created successfully', 'order_id': order_id}), 201


# Проверка наличия файла и создание пустого файла при необходимости
if not os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    app.run(port=5003, debug=True)
