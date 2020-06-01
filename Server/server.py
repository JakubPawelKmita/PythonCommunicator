import mysql.connector
import socket
import select
import json
import hashlib

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


class Response:
    head = None
    body = None
    dict = None

    def __init__(self):
        pass

    def register(self, succeed, msg):
        self.dict = {
            "action": "register",
            "succeed": succeed,
            "msg": msg
        }

    def login(self, succeed, msg):
        self.dict = {
            "action": "login",
            "succeed": succeed,
            "msg": msg
        }

    def logout(self, succeed, msg):
        self.dict = {
            "action": "logout",
            "succeed": succeed,
            "msg": msg
        }

    def get_chats(self, succeed, msg, chats):
        self.dict = {
            "action": "get_chats",
            "succeed": succeed,
            "msg": msg,
            "chats": chats
        }

    def create_chat(self, succeed, msg, chat):
        self.dict = {
            "action": "create_chat",
            "succeed": succeed,
            "msg": msg,
            "chat": chat
        }

    def add_to_chat(self, succeed, msg):
        self.dict = {
            "action": "add_to_chat",
            "succeed": succeed,
            "msg": msg
        }

    def new_msg(self, succeed, msg):
        self.dict = {
            "action": "new_msg",
            "succeed": succeed,
            "msg": msg
        }

    def chat_update(self, login, chat, msg):
        self.dict = {
            "action": "chat_update",
            "login": login,
            "chat": chat,
            "msg": msg
        }

    def get_users(self, succeed, msg, user_list):
        self.dict = {
            "action": "get_users",
            "succeed": succeed,
            "msg": msg,
            "user_list": user_list
        }

    def get_msgs(self, succeed, msg, chat_msgs):
        self.dict = {
            "action": "get_msgs",
            "succeed": succeed,
            "msg": msg,
            "chat_msgs": chat_msgs
        }

    def dummy_answer(self, msg):
        self.dict = {
            "action": "failed action",
            "succeed": False,
            "msg" : msg
        }

    def get_prepared_response(self):
        self.body = json.dumps(self.dict).encode('utf-8')
        self.head = f"{len(self.body):<{HEADER_LENGTH}}".encode('utf-8')
        return self.head + self.body


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return client_socket.recv(message_length).decode('utf-8')

    except Exception as e:
        return False


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    db="pychatdb"
)

response = Response()

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
                    del id_user[user_id[notified_socket]]
                    del user_id[notified_socket]
                except KeyError:
                    print("Client was not logged")
                continue

            # request processing
            print('New request from {}:{} > {}'.format(*clients[notified_socket], message))
            req = json.loads(message)
            if not user_id or notified_socket not in user_id.keys() or user_id[notified_socket] is None: #User not logged
                print("User not logged")
                #Operacje dostepne dla niezalogowanego usera: login, register
                if req["action"] == "register":
                    cur.execute(f'SELECT login FROM users WHERE login = "{req["login"]}"')
                    if len(cur.fetchall()) == 0:
                        print("INSERT new user")
                        p = req["password"]
                        sql = "INSERT INTO users (login, password, email, islogged) VALUES (%s, %s, %s, %s)"
                        val = (req["login"], hashlib.sha256(p.encode()).hexdigest(), req["email"], 0)
                        cur.execute(sql, val)
                        mydb.commit()
                        print(cur.rowcount, "record inserted.")

                        response.register(True, None)
                        notified_socket.send(response.get_prepared_response())
                    else:
                        print("user with this login already exists!")
                        response.register(False, "user with this login already exists")
                        notified_socket.send(response.get_prepared_response())

                elif req["action"] == "login":
                    cur.execute(f'SELECT login FROM users WHERE login = "{req["login"]}"')
                    query_result = cur.fetchall()
                    if not query_result or len([query_result[0][0]]) == 0:
                        print("user doesn't exist")
                        response.login(False, "user doesn't exist")
                        notified_socket.send(response.get_prepared_response())
                    else:
                        password = hashlib.sha256(req["password"].encode()).hexdigest()
                        sql = 'SELECT id, login, password, islogged  FROM users WHERE login = %s AND password = %s'
                        val = (req["login"], password)
                        cur.execute(sql, val)
                        result = cur.fetchall()

                        if len(result) == 0:
                            print("incorrect password")
                            response.login(False, "incorrect password")
                            notified_socket.send(response.get_prepared_response())
                        elif result[0][3] == 1:
                            print("user already logged")
                            response.login(False, "user already logged")
                            notified_socket.send(response.get_prepared_response())
                        else:
                            print(f"user with id: {result[0][0]} logged in")

                            sql = 'SELECT id, login, password, islogged  FROM users WHERE login = %s AND password = %s'
                            val = (req["login"], password)
                            cur.execute(sql, val)
                            result = cur.fetchall()
                            print(f"user with id: {result[0][0]}, islogged {result[0][3]} logged in")

                            q = 'UPDATE users SET islogged = 1 WHERE login = %s AND password = %s'
                            cur.execute(q, (result[0][1], password))

                            mydb.commit()

                            sql = 'SELECT id, login, password, islogged  FROM users WHERE login = %s AND password = %s'
                            val = (req["login"], password)
                            cur.execute(sql, val)
                            result = cur.fetchall()
                            print(f"user with id: {result[0][0]}, islogged {result[0][3]} logged in")

                            user_id[notified_socket] = result[0][0]
                            id_user[result[0][0]] = notified_socket

                            response.login(True, None)
                            notified_socket.send(response.get_prepared_response())
                else:
                    response.dummy_answer("Operations supported for not logged users: register, login")
                    notified_socket.send(response.get_prepared_response())
            else:
                print("User ", user_id[notified_socket], " logged")
                if req["action"] == "logout":
                    try:
                        cur.execute(f"SELECT login FROM users WHERE id = {user_id[notified_socket]}")
                        result = cur.fetchall()
                        if len(result) == 1:
                            cur.execute(f"UPDATE users SET islogged = 0 WHERE id = {user_id[notified_socket]}")
                            mydb.commit()
                            user_id[notified_socket] = None
                            response.login(True, "Logout completed - current user is None")
                            notified_socket.send(response.get_prepared_response())

                    except KeyError:
                        print("Client is not logged")
                        response.get_chats(False, "You are not logged", None)
                        notified_socket.send(response.get_prepared_response())

                elif req["action"] == "get_chats":
                    try:
                        cur.execute(f"SELECT chat FROM chatmember WHERE user = {user_id[notified_socket]}")
                        result = cur.fetchall()
                        if len(result) == 0:
                            response.get_chats(True, "You are not added to any chat", None)
                            notified_socket.send(response.get_prepared_response())
                        else:
                            chats = []
                            for row in result:
                                chats.append(row[0])
                            response.get_chats(True, None, chats)
                            notified_socket.send(response.get_prepared_response())
                    except KeyError:
                        print("Client is not logged")
                        response.get_chats(False, "You are not logged", None)
                        notified_socket.send(response.get_prepared_response())

                elif req["action"] == "create_chat":
                    try:
                        cur.execute(
                            f'INSERT INTO chats (creator, creationtime) VALUES ({user_id[notified_socket]}, CURRENT_TIMESTAMP )')
                        mydb.commit()
                        print(cur.rowcount, "record inserted.")

                        cur.execute(
                            f'SELECT id FROM chats WHERE creator = {user_id[notified_socket]} ORDER BY creationtime DESC LIMIT 1')
                        result = cur.fetchall()

                        response.create_chat(True, None, result[0][0])
                        notified_socket.send(response.get_prepared_response())

                    except KeyError:
                        print("Client is not logged")
                        response.create_chat(False, "You are not logged", None)
                        notified_socket.send(response.get_prepared_response())

                elif req["action"] == "add_to_chat":
                    try:
                        chat = int(req["chat"])

                        cur.execute(
                            f'SELECT * FROM chats WHERE creator = {user_id[notified_socket]} AND id = {chat}')
                        if len(cur.fetchall()) == 0:
                            response.add_to_chat(False, "You are not a creator of this chat")
                            raise Exception("Not a creator")

                        cur.execute(f'SELECT id FROM users WHERE login = "{req["login"]}"')
                        result = cur.fetchall()
                        if len(result) == 0:
                            response.add_to_chat(False, "User with this login doesn't exist")
                            raise Exception("User with this login doesn't exist")

                        user_to_add = result[0][0]

                        cur.execute(f'SELECT * FROM chatmember WHERE chat = {chat} AND user = {user_to_add}')
                        if not len(cur.fetchall()) == 0:
                            response.add_to_chat(False, "User is already in this chat")
                            raise Exception("User is already in this chat")

                        cur.execute(f'INSERT INTO chatmember (chat, user) VALUES ({chat}, {user_to_add})')
                        mydb.commit()
                        print(cur.rowcount, "record inserted.")
                        response.add_to_chat(True, None)

                    except KeyError:
                        print("Client is not logged")
                        response.add_to_chat(False, "You are not logged")
                    except ValueError:
                        print("chat must be an integer")
                        response.add_to_chat(False, "chat must be an integer")
                    except Exception as e:
                        print(e)
                    finally:
                        notified_socket.send(response.get_prepared_response())

                elif req["action"] == "new_msg":
                    try:
                        user = user_id[notified_socket]
                        chat = int(req["chat"])
                        msg = req["msg"]

                        cur.execute(f'SELECT * FROM chatmember WHERE chat = {chat} AND user = {user}')
                        if len(cur.fetchall()) == 0:
                            response.new_msg(False, "You are not a member of this chat")
                            raise Exception("Not a member")

                        cur.execute(f'SELECT login FROM users WHERE id = {user}')
                        login = cur.fetchall()[0][0]
                        response.chat_update(login, chat, msg)

                        cur.execute(f'SELECT user FROM chatmember WHERE chat = {chat}')
                        members = cur.fetchall()

                        # This for-loop sends chat_update to all logged members of the chat
                        for member in members:
                            try:
                                id_user[member[0]].send(response.get_prepared_response())
                            except KeyError:
                                continue

                        cur.execute(
                            f'INSERT INTO messages (user, chat, time, msg) VALUES ({user}, {chat}, CURRENT_TIMESTAMP, "{msg}")')
                        mydb.commit()
                        print(cur.rowcount, "record inserted.")
                        response.new_msg(True, None)

                    except KeyError:
                        print("Client is not logged")
                        response.new_msg(False, "You are not logged")
                    except ValueError:
                        print("chat must be an integer")
                        response.new_msg(False, "chat must be an integer")
                    finally:
                        notified_socket.send(response.get_prepared_response())

                elif req["action"] == "get_users":
                    try:
                        user = user_id[notified_socket]
                        cur.execute('SELECT login FROM users')
                        user_list = []
                        users = cur.fetchall()
                        for u in users:
                            user_list.append(u[0])
                        response.get_users(True, None, user_list)
                    except KeyError:
                        print("Client is not logged")
                        response.get_users(False, "You are not logged", None)
                    finally:
                        notified_socket.send(response.get_prepared_response())

                elif req["action"] == "get_msgs":
                    try:
                        user = user_id[notified_socket]
                        chat = int(req["chat"])
                        counter = int(req["counter"])
                        how_many = int(req["how_many"])

                        cur.execute(f'SELECT * FROM chatmember WHERE chat = {chat} AND user = {user}')
                        if len(cur.fetchall()) == 0:
                            response.get_msgs(False, "You are not a member of this chat", None)
                            raise Exception("Not a member")

                        cur.execute(
                            f'SELECT login, msg FROM messages INNER JOIN users ON messages.user = users.id WHERE chat = {chat} ORDER BY time DESC LIMIT {counter}, {how_many}')
                        chat_msgs = cur.fetchall()
                        response.get_msgs(True, None, chat_msgs)
                    except KeyError:
                        print("Client is not logged")
                        response.get_msgs(False, "You are not logged", None)
                    except ValueError:
                        print("chat, counter and how_many must be the integers")
                        response.get_msgs(False, "chat, counter and how_many must be the integers", None)
                    except Exception as e:
                        print(e)
                    finally:
                        notified_socket.send(response.get_prepared_response())

                else:
                    response.dummy_answer("This operation is not supported for logged users")
                    notified_socket.send(response.get_prepared_response())

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