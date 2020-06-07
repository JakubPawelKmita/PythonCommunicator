import json


class RespClass:
    head = None
    body = None
    dict = None
    HEADER_LENGTH = 10

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

    def get_chat_members(self, succeed, msg, members):
        self.dict = {
            "action": "get_chat_members",
            "succeed": succeed,
            "msg": msg,
            "members": members
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
            "msg": msg
        }

    def get_prepared_response(self):
        self.body = json.dumps(self.dict).encode('utf-8')
        self.head = f"{len(self.body):<{self.HEADER_LENGTH}}".encode('utf-8')
        return self.head + self.body
