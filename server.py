import socket
import threading
import json
import os

# Настройки сервера
HOST = '0.0.0.0'  # Сервер будет слушать на всех интерфейсах
PORT = 5000
DATA_FILE = 'data.json'  # Файл для хранения пользователей и сообщений

# Создаем файл данных, если его нет
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({'users': {}, 'messages': []}, f)

def load_data():
    """Загружает данные из JSON файла."""
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    """Сохраняет данные в JSON файл."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        try:
            message = conn.recv(1024).decode('utf-8')
            if not message:
                break

            print(f"[RECEIVED] {message} from {addr}")

            # Обработка команд от клиента
            request = json.loads(message)
            response = process_request(request)

            # Отправка ответа клиенту
            conn.send(json.dumps(response).encode('utf-8'))

        except Exception as e:
            print(f"[ERROR] {e}")
            break

    conn.close()

def process_request(request):
    """Обрабатывает запросы клиентов."""
    data = load_data()
    if request['action'] == 'register':
        username = request['username']
        password = request['password']
        if username in data['users']:
            return {'status': 'error', 'message': 'Username already exists.'}
        else:
            data['users'][username] = {'password': password, 'status': 'offline'}
            save_data(data)
            return {'status': 'success', 'message': 'Registration successful.'}

    elif request['action'] == 'login':
        username = request['username']
        password = request['password']
        if username not in data['users']:
            return {'status': 'error', 'message': 'User not found.'}
        if data['users'][username]['password'] != password:
            return {'status': 'error', 'message': 'Incorrect password.'}
        data['users'][username]['status'] = 'online'
        save_data(data)
        return {'status': 'success', 'message': 'Login successful.'}

    elif request['action'] == 'send_message':
        username = request['username']
        message = request['message']
        data['messages'].append({'username': username, 'message': message})
        save_data(data)
        return {'status': 'success', 'message': 'Message sent.'}

    elif request['action'] == 'get_messages':
        return {'status': 'success', 'messages': data['messages']}

    elif request['action'] == 'logout':
        username = request['username']
        if username in data['users']:
            data['users'][username]['status'] = 'offline'
            save_data(data)
        return {'status': 'success', 'message': 'Logout successful.'}

    else:
        return {'status': 'error', 'message': 'Invalid action.'}

def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[STARTING] Server is starting on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start()
