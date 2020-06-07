import mysql.connector
import socket
import select
import json
from datetime import datetime

from PythonCommunicator.Server.response import RespClass
from PythonCommunicator.Server.server_support import ServerSupport

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()
sockets_list = [server_socket]
clients = {}  # client_socket -> client_address
user_id = {}  # client_socket -> user_id in database after login operation
id_user = {}  # user_id -> client_socket after login operation
print(f'Listening for connections on {IP}:{PORT}...')


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return client_socket.recv(message_length).decode('utf-8')

    except Exception as e:
        return False


def update_lastaction_time(user_id):
    lastactionsql = f"UPDATE users set lastaction = %s where id = %s"
    cur.execute(lastactionsql, (datetime.now(), user_id))
    mydb.commit()


def logout_action(msg):
    resp = RespClass()
    try:
        cur.execute(f"SELECT login FROM users WHERE id = {user_id[notified_socket]}")
        result = cur.fetchall()
        if len(result) == 1:
            cur.execute(f"UPDATE users SET islogged = 0 WHERE id = {user_id[notified_socket]}")
            mydb.commit()
            user_id[notified_socket] = None
            resp.logout(True, msg)
            notified_socket.send(resp.get_prepared_response())

    except KeyError:
        print("Client is not logged")
        resp.get_chats(False, "You are not logged", None)
        notified_socket.send(resp.get_prepared_response())


def logout_client_after_close(user_to_logout_id):
    try:
        cur.execute(f"SELECT login FROM users WHERE id = {user_to_logout_id}")
        result = cur.fetchall()
        if len(result) == 1:
            cur.execute(f"UPDATE users SET islogged = 0 WHERE id = {user_to_logout_id}")
            mydb.commit()

    except KeyError:
        print("Client is not logged22222")

mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    passwd="root",
    db="pychatdb",
    port=3307
)
cur = mydb.cursor()

# mydb.close()

cur.execute(f'UPDATE users SET islogged = 0')
mydb.commit()

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        # Nowy klient dołącza do serwera
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            sockets_list.append(client_socket)
            clients[client_socket] = client_address
            print('Accepted new connection from {}:{}'.format(*clients[client_socket]))
        # odbieramy wiadomość z socketu
        else:
            message = receive_message(notified_socket)

            # closing connection
            if message is False:
                print('Closed connection from {}:{}'.format(*clients[notified_socket]))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                try:
					if user_id[notified_socket] is not None:
						logout_client_after_close(user_id[notified_socket])
                    del id_user[user_id[notified_socket]]
                    del user_id[notified_socket]
                except KeyError:
                    print("Client was not logged")
                continue

            # request processing
            print('New request from {}:{} > {}'.format(*clients[notified_socket], message))
            req = json.loads(message)
            if not user_id or notified_socket not in user_id.keys() or user_id[
                notified_socket] is None:  # User not logged
                print("User not logged")
                # Operacje dostepne dla niezalogowanego usera: login, register
                if req["action"] == "register":
                    ServerSupport.register(cur, req, mydb, notified_socket)

                elif req["action"] == "login":
                    ServerSupport.login(cur, notified_socket, req, mydb, user_id, id_user)
                else:
                    r = RespClass()
                    r.dummy_answer("Operations supported for not logged users: register, login")
                    notified_socket.send(r.get_prepared_response())
            else:
                print("User ", user_id[notified_socket], " logged")
                last_action_time = ServerSupport().get_lastaction_difference(user_id[notified_socket], cur)
                if last_action_time:
                    update_lastaction_time(user_id[notified_socket])
                    logout_msg = "Logout completed - timeout is reached"
                    logout_action(logout_msg)
                    continue
                update_lastaction_time(user_id[notified_socket])
                if req["action"] == "logout":
                    logout_msg = "Logout completed - current user is None"
                    ServerSupport().logout_acion(logout_msg, cur, mydb, user_id, notified_socket)

                elif req["action"] == "get_chats":
                    ServerSupport().get_chats(cur, user_id, notified_socket)

                elif req["action"] == "get_chat_members":
                    ServerSupport.get_chat_members(cur, user_id, notified_socket, req)

                elif req["action"] == "create_chat":
                    ServerSupport().create_chat(cur, user_id, notified_socket, mydb)

                elif req["action"] == "add_to_chat":
                    ServerSupport().add_to_chat(req, cur, user_id, notified_socket, mydb)

                elif req["action"] == "new_msg":
                    ServerSupport().new_msg(cur, user_id, notified_socket, id_user, req, mydb)

                elif req["action"] == "get_users":
                    ServerSupport.get_users(cur, notified_socket)

                elif req["action"] == "get_msgs":
                    ServerSupport.get_msgs(cur, user_id, notified_socket, req)

                else:
                    r = RespClass()
                    r.dummy_answer("This operation is not supported for logged users")
                    notified_socket.send(r.get_prepared_response())

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
        try:
            del id_user[user_id[notified_socket]]
            del user_id[notified_socket]
        except KeyError:
            print("Client was not logged")
        continue
mydb.close()
