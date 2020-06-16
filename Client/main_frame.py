import tkinter as tk
import json

from chat_page import ChatPage
from welcome_page import WelcomePage
from register_page import RegisterPage
from chat_panel import ChatPanel
from create_chat_panel import CreateChatPanel
from add_user import AddUserToChat
from member_page import MembersPage

class MainFrame(tk.Tk):

    def __init__(self, client_socket, request):
        self.client_socket = client_socket
        self.request = request
        
        tk.Tk.__init__(self)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (WelcomePage, RegisterPage, ChatPanel, CreateChatPanel, ChatPage, AddUserToChat, MembersPage):
            frame = F(container, self, client_socket, request)

            self.frames[F.__name__] = frame

            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("WelcomePage")

    def show_frame(self, cont):
        self.frame = self.frames[cont]
        if cont == "ChatPanel":
            self.frame.get_chats()
        elif cont in ["CreateChatPanel", "AddUserToChat", "MembersPage"]:
            self.frame.get_users()
        self.frame.set_title_frame()
        self.frame.tkraise()

    def make_update(self, message):
        try:
            print(message, type(message))
            parsed_msg = json.loads(message)
            self.frame.message_arrived(parsed_msg)
        except Exception as e:
            print("Sorry server something is wrong with your message: {}".format(e))