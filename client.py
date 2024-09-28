import socket
import json

# Настройки клиента
HOST = '10.5.173.65'  # IP-адрес сервера
PORT = 5000

def send_request(sock, request):
    """Отправляет запрос на сервер и получает ответ."""
    sock.send(json.dumps(request).encode('utf-8'))
    response = json.loads(sock.recv(1024).decode('utf-8'))
    return response

def register(sock):
    """Регистрация нового пользователя."""
    username = input("Enter username: ")
    password = input("Enter password: ")
    request = {
        'action': 'register',
        'username': username,
        'password': password
    }
    response = send_request(sock, request)
    print(response['message'])

def login(sock):
    """Вход в систему."""
    username = input("Enter username: ")
    password = input("Enter password: ")
    request = {
        'action': 'login',
        'username': username,
        'password': password
    }
    response = send_request(sock, request)
    print(response['message'])
    return response['status'] == 'success'

def send_message(sock, username):
    """Отправка сообщения."""
    message = input("Enter your message: ")
    request = {
        'action': 'send_message',
        'username': username,
        'message': message
    }
    response = send_request(sock, request)
    print(response['message'])

def get_messages(sock):
    """Получение всех сообщений."""
    request = {'action': 'get_messages'}
    response = send_request(sock, request)
    for msg in response['messages']:
        print(f"[{msg['username']}] {msg['message']}")

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    while True:
        choice = input("Choose action (register/login/exit): ").strip().lower()
        if choice == 'register':
            register(sock)
        elif choice == 'login':
            if login(sock):
                username = input("Enter your username to continue: ")
                while True:
                    action = input("Choose action (send/get/logout): ").strip().lower()
                    if action == 'send':
                        send_message(sock, username)
                    elif action == 'get':
                        get_messages(sock)
                    elif action == 'logout':
                        request = {'action': 'logout', 'username': username}
                        response = send_request(sock, request)
                        print(response['message'])
                        break
                    else:
                        print("Invalid action.")
            else:
                print("Login failed.")
        elif choice == 'exit':
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

    sock.close()

if __name__ == '__main__':
    main()
