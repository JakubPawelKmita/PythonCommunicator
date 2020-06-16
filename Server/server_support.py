from datetime import datetime
import hashlib
from PythonCommunicator.Server.response import RespClass


def anti_drop(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


class ServerSupport:
    @staticmethod
    def update_lastaction_time(user_id, cur, mydb):
        lastactionsql = f"UPDATE users set lastaction = %s where id = %s"
        cur.execute(lastactionsql, (datetime.now(), user_id))
        mydb.commit()

    @staticmethod
    def get_lastaction_difference(user_id, cur):
        cur.execute(f'SELECT lastaction FROM users WHERE id = "{user_id}"')
        result = cur.fetchall()
        minute_diff = (datetime.now() - result[0][0]).seconds / 60
        if minute_diff > float(datetime.now().replace(hour=0, minute=15, second=0, microsecond=0).minute):
            return True
        return False

    @staticmethod
    def register(cur, req, mydb, notified_socket):
        response = RespClass()
        if req["login"] == anti_drop(req["login"]) and req["email"] == anti_drop(req["email"]):
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
        else:
            response.register(False, "not aloowed signs (\" or \\) in login or email")
            notified_socket.send(response.get_prepared_response())

    @staticmethod
    def login(cur, notified_socket, req, mydb, user_id, id_user):

        req["login"] = anti_drop(req["login"])
        cur.execute(f'SELECT login FROM users WHERE login = "{req["login"]}"')
        query_result = cur.fetchall()
        response = RespClass()
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

                sql = 'SELECT id, login, password, islogged  FROM users WHERE login = %s AND password = %s'
                val = (req["login"], password)
                cur.execute(sql, val)
                result = cur.fetchall()

                q = 'UPDATE users SET islogged = 1 WHERE login = %s AND password = %s'
                cur.execute(q, (result[0][1], password))

                mydb.commit()

                sql = 'SELECT id, login, password, islogged  FROM users WHERE login = %s AND password = %s'
                val = (req["login"], password)
                cur.execute(sql, val)
                result = cur.fetchall()

                user_id[notified_socket] = result[0][0]
                id_user[result[0][0]] = notified_socket

                ServerSupport.update_lastaction_time(result[0][0], cur, mydb)
                response.login(True, None)
                notified_socket.send(response.get_prepared_response())

    @staticmethod
    def logout_acion(msg, cur, mydb, user_id, notified_socket):
        response = RespClass()
        try:
            cur.execute(f"SELECT login FROM users WHERE id = {user_id[notified_socket]}")
            result = cur.fetchall()
            if len(result) == 1:
                cur.execute(f"UPDATE users SET islogged = 0 WHERE id = {user_id[notified_socket]}")
                mydb.commit()
                user_id[notified_socket] = None
                response.logout(True, msg)
                notified_socket.send(response.get_prepared_response())

        except KeyError:
            print("Client is not logged")
            response.get_chats(False, "You are not logged", None)
            notified_socket.send(response.get_prepared_response())

    @staticmethod
    def get_chat_members(cur, user_id, notified_socket, req):
        response = RespClass()
        try:
            chat = int(req["chat"])
            cur.execute(f"SELECT chat FROM chatmember WHERE user = {user_id[notified_socket]} AND chat = {chat}")
            result = cur.fetchall()
            if len(result) == 0:
                response.get_chat_members(False, "You are not a member of this chat", None)
                raise Exception("Not a member")
            cur.execute(
                f'SELECT login FROM users INNER JOIN chatmember ON users.id = chatmember.user WHERE chat = {chat}')
            members = cur.fetchall()
            member_list = []
            for m in members:
                member_list.append(m[0])
            response.get_chat_members(True, None, member_list)
        except KeyError:
            print("Client is not logged")
            response.get_chat_members(False, "You are not logged", None)
        except ValueError:
            print("chat must be an integer")
            response.get_chat_members(False, "chat must be an integer", None)
        except Exception as e:
            print(e)
        finally:
            notified_socket.send(response.get_prepared_response())

    @staticmethod
    def get_chats(cur, user_id, notified_socket):
        response = RespClass()
        try:
            cur.execute(f"SELECT chat FROM chatmember WHERE user = {user_id[notified_socket]} order by chat")
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

    @staticmethod
    def create_chat(cur, user_id, notified_socket, mydb):
        response = RespClass()
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

    @staticmethod
    def add_to_chat(req, cur, user_id, notified_socket, mydb, id_user):
        response = RespClass()
        try:
            req["login"] = anti_drop(req["login"])
            chat = int(req["chat"])

            cur.execute(
                f'SELECT * FROM chats WHERE creator = {user_id[notified_socket]} AND id = {chat}')
            res = cur.fetchall()
            if len(res) == 0:
                response.add_to_chat(False, "You are not a creator of this chat")
                # response.add_to_chat(False, "You are not a creator of this chat")
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

            try:
                ServerSupport.get_chats(cur, user_id, id_user[user_to_add])
            except KeyError:
                pass

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

    @staticmethod
    def new_msg(cur, user_id, notified_socket, id_user, req, mydb):
        response = RespClass()
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

            msg = anti_drop(msg)

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

    @staticmethod
    def get_users(cur, notified_socket):
        response = RespClass()
        try:
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

    @staticmethod
    def get_msgs(cur, user_id, notified_socket, req):
        response = RespClass()
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
