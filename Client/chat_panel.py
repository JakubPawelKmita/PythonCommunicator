import tkinter as tk
from tkinter import ttk

LARGE_FONT= ("Verdana", 12)

class ChatPanel(tk.Frame):

    def __init__(self, parent, controller, client_socket, request):
        self.client_socket = client_socket
        self.parent = parent
        self.controller = controller
        self.request = request

        tk.Frame.__init__(self, parent)
        self.winfo_toplevel().minsize(400, 300)
        windowWidth = self.winfo_toplevel().winfo_reqwidth()
        windowHeight = self.winfo_toplevel().winfo_reqheight()

        positionRight = int(self.winfo_toplevel().winfo_screenwidth()/2 - windowWidth)
        positionDown = int(self.winfo_toplevel().winfo_screenheight()/2 - windowHeight)
        self.winfo_toplevel().geometry("+{}+{}".format(positionRight, positionDown))

        self.winfo_toplevel().title("Chat Panel")

        label_details = tk.Label(self, text="Please choose the chat, that you want to join: ", font=LARGE_FONT)
        label_details.pack(pady=10, padx=10)

        self.choosen_chat = tk.StringVar() 
        self.error_chats_load = tk.StringVar() 
        self.chats = ttk.Combobox(self, width = 27, textvariable = self.choosen_chat, state="readonly", postcommand = self.get_chats) 
        
        self.chats['values'] = () 
        self.chats.pack(pady=10, padx=10)

        label_error_chats_load = tk.Label(self, textvariable=self.error_chats_load, fg="red")
        label_error_chats_load.pack()

        start_button = tk.Button(self, text="Start Chat", width=20, height=1, command = self.start_chat)
        start_button.pack(pady=10, padx=10)

        create_button = tk.Button(self, text="Create Chat", width=20, height=1, command = self.create_chat)
        create_button.pack(pady=10, padx=10)

        back_button = tk.Button(self, text="Log out", width=20, height=1, command = self.back_to_startpage)
        back_button.pack(pady=10, padx=10)

    def get_chats(self):
        self.request.get_chats()
        self.client_socket.send_message(self.request.get_prepared_request())

    def start_chat(self):
        if self.choosen_chat.get():
            self.controller.show_frame("ChatPage")
            self.controller.chat_id = self.choosen_chat.get()
            self.request.get_msgs(self.choosen_chat.get(), 0, 10)
            self.client_socket.send_message(self.request.get_prepared_request())

    def back_to_startpage(self):
        self.clean_everything()
        self.controller.show_frame("WelcomePage")

    def create_chat(self):
        self.clean_everything()
        self.controller.show_frame("CreateChatPanel")

    def message_arrived(self, message):
        if message["action"] == "get_chats":
            msg = message["msg"]
            if message["succeed"] == True and message["chats"] is None:
                self.chats['values'] = ()
                self.choosen_chat.set('')
                self.error_chats_load.set(msg)
            elif message["succeed"] == True and message["chats"] is not None:
                self.chats['values'] =  message["chats"]
                self.chats.current(0)
                self.error_chats_load.set('')
    
    def clean_everything(self):
        self.choosen_chat.set('')
        self.error_chats_load.set('')

    def set_title_frame(self):
        self.winfo_toplevel().title("Chat Panel")