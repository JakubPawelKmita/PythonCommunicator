import socket
import select
import errno
import sys
import tkinter as tk
from tkinter import ttk 
import json

from request import Request
from main_frame import MainFrame

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

class Client(object):
    client_socket = None
    client_name = None

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((IP, PORT))
        self.client_socket.setblocking(False)

    def send_message(self, message):
        self.client_socket.send(message)

    def receive_message(self, message):
        return self.client_socket.recv(message)

    def set_client_name(self, name):
        self.client_name = name

    def get_client_name(self):
        return self.client_name


def main():
    request = Request()
    client = Client()
    app = MainFrame(client, request)
    while True:
        try:
            app.update()
            header = client.receive_message(HEADER_LENGTH)
            if not len(header):
                print('Connection closed by the server')
                sys.exit()
            msg_length = int(header.decode('utf-8').strip())
            msg = client.receive_message(msg_length).decode('utf-8')
            print("    RESPONSE: " + msg)
            app.make_update(msg)
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()
            continue
        except tk.TclError as e:
            print("Bye!")
            sys.exit()
        except Exception as e:
            print('Reading error: '.format(str(e)))
            sys.exit()
    

if __name__ == "__main__":
    main()