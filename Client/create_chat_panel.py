import tkinter as tk
from tkinter import messagebox as mb


class CreateChatPanel(tk.Frame):

    def __init__(self, parent, controller, client_socket, request):
        self.users = []
        self.checkboxes = {}
        self.client_socket = client_socket
        self.parent = parent
        self.controller = controller
        self.request = request

        tk.Frame.__init__(self, parent)
        self.winfo_toplevel().minsize(400, 300)
        windowWidth = self.winfo_toplevel().winfo_reqwidth()
        windowHeight = self.winfo_toplevel().winfo_reqheight()

        positionRight = int(self.winfo_toplevel().winfo_screenwidth() / 2 - windowWidth)
        positionDown = int(self.winfo_toplevel().winfo_screenheight() / 2 - windowHeight)
        self.winfo_toplevel().geometry("+{}+{}".format(positionRight, positionDown))

        self.winfo_toplevel().title("Chat Creation Panel")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        label_details = tk.Label(self, text="Please choose the chatmembers from list:", font=("Times New Roman", 16))
        label_details.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.error_user_load = tk.StringVar()
        self.error_chat_create = tk.StringVar()
        self.error_user_add = tk.StringVar()

        self.vsb = tk.Scrollbar(self, orient="vertical")
        self.text = tk.Text(self, width=40, height=10,
                            yscrollcommand=self.vsb.set)
        self.vsb.config(command=self.text.yview)
        self.vsb.grid(row=1, column=1, sticky="nsew", padx=2, pady=2)
        self.text.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        label_error_usser_load = tk.Label(self, textvariable=self.error_user_load, fg="red")
        label_error_usser_load.grid(row=2, column=0, sticky="nsew", padx=2, pady=2)

        create_button = tk.Button(self, text="Create Chat", width=20, height=2, command=self.create_chat, font=("Times New Roman", 14))
        create_button.grid(row=3, column=0, sticky="nsew", columnspan=2, padx=2, pady=2)

        self.label_error_chat_create = tk.Label(self, textvariable=self.error_chat_create, fg="red")
        self.label_error_chat_create.grid(row=4, column=0, sticky="nsew", padx=2, pady=2)

        label_error_user_add = tk.Label(self, textvariable=self.error_user_add, fg="red")
        label_error_user_add.grid(row=5, column=0, sticky="nsew", padx=2, pady=2)

        back_chat_panel_button = tk.Button(self, text="Back to Chat Panel", width=20, height=2, font=("Times New Roman", 14),
                                           command=self.back_to_chatpanel)
        back_chat_panel_button.grid(row=6, column=0, sticky="nsew", columnspan=2, padx=2, pady=2)

        back_button = tk.Button(self, text="Log out", width=20, height=2, command=self.logout, font=("Times New Roman", 14))
        back_button.grid(row=7, column=0, sticky="nsew",columnspan=2, padx=2, pady=2)

    def get_users(self):
        self.request.get_users()
        self.client_socket.send_message(self.request.get_prepared_request())

    def fill_users(self):
        self.text.configure(state='normal')
        self.text.delete("1.0", tk.END)
        self.text.configure(state='disabled')
        self.checkboxes = {}
        for u in self.users:
            if u != self.controller.client_socket.get_client_name():
                cv = tk.IntVar()
                cb = tk.Checkbutton(self, text="", variable=cv, onvalue=1, offvalue=0)
                self.checkboxes[u] = cv
                self.text.configure(state='normal')
                self.text.window_create("end", window=cb)
                self.text.insert("end", u + "\n")
                self.text.configure(state='disabled')

    def clean_users(self):
        self.fill_users()

    def clean_errors(self):
        self.error_user_load.set("")
        self.error_chat_create.set("")
        self.error_user_add.set("")

    def clean_everything(self):
        self.clean_users()
        self.clean_errors()

    def back_to_chatpanel(self):
        self.controller.show_frame("ChatPanel")
        self.clean_everything()

    def back_to_startpage(self):
        self.controller.show_frame("WelcomePage")
        self.clean_everything()

    def logout(self):
        self.request.logout()
        self.client_socket.send_message(self.request.get_prepared_request())
        self.back_to_startpage()

    def create_chat(self):
        checks = [i.get() for i in self.checkboxes.values()]
        if 1 in checks:
            self.request.create_chat()
            self.client_socket.send_message(self.request.get_prepared_request())
        else:
            self.error_chat_create.set("You have to add at least one member to chat!")

    def show_timeout_message(self):
        mb.showerror("Logout", "Logout completed - timeout is reached")

    def message_arrived(self, message):
        msg = message["msg"]
        if message["action"] == "logout" and message["msg"] == "Logout completed - timeout is reached":
            self.show_timeout_message()
            self.back_to_startpage()

        if message["action"] == "get_users":
            if message["succeed"] == True and message['user_list'] is None:
                self.users = []
                self.clean_errors()
                self.error_user_load.set(msg)
            elif message["succeed"] == True and message['user_list'] is not None:
                self.users = message['user_list']
                self.fill_users()
                self.clean_errors()
                self.error_user_load.set('')
            else:
                self.clean_errors()
                self.error_user_load.set(msg)
        elif message["action"] == "create_chat":
            if message["succeed"] == True:
                self.created_chat = message["chat"]
                for u, c in self.checkboxes.items():
                    if c.get() == 1:
                        self.request.add_to_chat(u, message['chat'])
                        self.client_socket.send_message(self.request.get_prepared_request())
                self.request.add_to_chat(self.controller.client_socket.get_client_name(), message['chat'])
                self.client_socket.send_message(self.request.get_prepared_request())
                self.error_user_load.set('')
            else:
                self.clean_errors()
                self.error_chat_create.set(msg)
        elif message["action"] == "add_to_chat":
            if message["succeed"] == True:
                self.clean_errors()
                self.error_chat_create.set(
                    "Chat created successfuly. \n The id of chat is: {}. Please remember it.".format(self.created_chat))
                self.label_error_chat_create["fg"] = "green"
            else:
                self.clean_errors()
                self.error_user_add.set(msg)

    def set_title_frame(self):
        self.winfo_toplevel().title("Chat Creation Panel")
