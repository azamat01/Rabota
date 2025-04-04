import json
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import os

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Отдаём файл index.html
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('templates/index.html', 'r') as f:
                self.wfile.write(f.read().encode())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/order':
            # Обрабатываем POST запрос
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            order_data = json.loads(post_data)

            username = order_data.get('username')
            item_id = order_data.get('item_id')

            # Логика для обработки заказа
            message = f"New order from {username} for item {item_id}"

            # Отправляем данные через шину данных (эмуляция)
            print(f"Message published to data bus: {message}")

            # Ответ на запрос
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'message': 'Order created'}
            self.wfile.write(json.dumps(response).encode())

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Page not found')

# Настроим сервер
def run(server_class=HTTPServer, handler_class=MyHandler):
    server_address = ('', 5003)  # Запуск на порту 5003
    httpd = server_class(server_address, handler_class)
    print("Server started on http://127.0.0.1:5003")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
