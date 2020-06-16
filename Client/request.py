import json 
HEADER_LENGTH = 10

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

    def get_chat_members(self, chat):
        self.dict = {
            "action": "get_chat_members",
            "chat": chat
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
