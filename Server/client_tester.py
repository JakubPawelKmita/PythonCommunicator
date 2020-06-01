import errno
import socket
import json
import sys
import threading
import time

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234


class Request:
    head = None
    body = None
    dict = None

    def __init__(self):
        pass

    def register(self, login, password, email):
        self.dict = {
            "action": "register",
            "login": login,  # string
            "password": password,  # string
            "email": email  # string
        }

    def login(self, login, password):
        self.dict = {
            "action": "login",
            "login": login,  # string
            "password": password  # string
        }

    def logout(self):
        self.dict = {
            "action": "logout"
        }	

    def get_chats(self):
        self.dict = {
            "action": "get_chats"
        }

    def create_chat(self):
        self.dict = {
            "action": "create_chat"
        }

    def add_to_chat(self, login, chat):
        self.dict = {
            "action": "add_to_chat",
            "login": login,  # string
            "chat": chat  # int (id of a chat)
        }

    def new_msg(self, chat, msg):
        self.dict = {
            "action": "new_msg",
            "chat": chat,  # int (id of a chat)
            "msg": msg  # string
        }

    def get_users(self):
        self.dict = {
            "action": "get_users"
        }

    def get_msgs(self, chat, counter, how_many):
        self.dict = {
            "action": "get_msgs",
            "chat": chat,  # int (id of a chat)
            "counter": counter,  # int (how many messages do you already have)
            "how_many": how_many  # int (how many messages you want)
        }

    def get_prepared_request(self):
        self.body = json.dumps(self.dict).encode('utf-8')
        self.head = f"{len(self.body):<{HEADER_LENGTH}}".encode('utf-8')
        return self.head + self.body


class Client(object):
    client_socket = None

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((IP, PORT))
        self.client_socket.setblocking(False)

    def send_message(self, message):
        self.client_socket.send(message)

    def receive_message(self, message):
        return self.client_socket.recv(message)


request = Request()
client = Client()


def read_socket():
    while True:
        try:
            header = client.receive_message(HEADER_LENGTH)
            if not len(header):
                print('Connection closed by the server')
                sys.exit()
            msg_length = int(header.decode('utf-8').strip())
            msg = client.receive_message(msg_length).decode('utf-8')
            print("    RESPONSE: " + msg)
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()
            continue
        except Exception as e:
            print('Reading error: {}'.format(str(e)))
            sys.exit()


def main():
    reader = threading.Thread(target=read_socket)
    reader.start()

    while True:
        time.sleep(0.1)
        command = input("command: ")

        if command == "register":
            request.register(input("  login: "), input("  password: "), input("  email: "))
            client.send_message(request.get_prepared_request())

        elif command == "login":
            request.login(input("  login: "), input("  password: "))
            client.send_message(request.get_prepared_request())

        elif command == "logout":
            request.logout()
            client.send_message(request.get_prepared_request())

        elif command == "get_chats":
            request.get_chats()
            client.send_message(request.get_prepared_request())

        elif command == "create_chat":
            request.create_chat()
            client.send_message(request.get_prepared_request())

        elif command == "add_to_chat":
            request.add_to_chat(input("  login: "), input("  chat: "))
            client.send_message(request.get_prepared_request())

        elif command == "new_msg":
            request.new_msg(input("  chat: "), input("  msg: "))
            client.send_message(request.get_prepared_request())

        elif command == "get_users":
            request.get_users()
            client.send_message(request.get_prepared_request())

        elif command == "get_msgs":
            request.get_msgs(input("  chat: "), input("  counter: "), input("  howmany: "))
            client.send_message(request.get_prepared_request())

        else:
            print("  List of commands:")
            print("    register       ")
            print("    login          ")
            print("    logout         ")
            print("    get_chats      ")
            print("    create_chat    ")
            print("    add_to_chat    ")
            print("    new_msg        ")
            print("    get_users      ")
            print("    get_msgs       ")


if __name__ == "__main__":
    main()
