import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# Функция для получения заказов с ордер-сервера
def get_orders():
    try:
        response = requests.get("http://localhost:5003/orders")  # Запрос на ордер-сервер
        if response.status_code == 200:
            return response.json().get("orders", [])
        else:
            print(f"Failed to fetch orders: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching orders: {e}")
        return []


# Функция для отправки статуса заказа в ордер-сервис через шину данных
def send_status_to_order_service(order_id, status):
    try:
        response = requests.post(
            "http://localhost:5003/order/response",  # Ордер-сервис
            json={"order_id": order_id, "status": status}
        )
        if response.status_code == 200:
            print("Order status updated successfully.")
        elif response.status_code == 404:
            print(f"Order with ID {order_id} not found.")
        else:
            print(f"Failed to update order status: {response.status_code}")
    except Exception as e:
        print(f"Error sending status to order service: {e}")


# Главная страница (главный HTML интерфейс)
@app.route('/')
def index():
    orders = get_orders()  # Получаем заказы с ордер-сервера
    return render_template('index.html', orders=orders)  # Передаем их в шаблон


# Обработка ответа на заказ
@app.route('/order/response', methods=['POST'])
def order_response():
    if request.is_json:
        order_id = request.json.get('order_id')  # Получаем order_id из JSON
        status = request.json.get('status')      # Получаем новый статус из JSON
    else:
        return jsonify({'message': 'Invalid Content-Type, must be application/json'}), 415

    if not order_id or not status:
        return jsonify({'message': 'Invalid data provided'}), 400

    # Отправляем запрос на ордер-сервис для обновления статуса
    send_status_to_order_service(order_id, status)

    return jsonify({'message': 'Order status updated successfully'}), 200


if __name__ == '__main__':
    app.run(port=5001, debug=True)
