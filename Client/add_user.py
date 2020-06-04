import tkinter as tk

LARGE_FONT= ("Verdana", 12)

class AddUserToChat(tk.Frame):

    def __init__(self, parent, controller, client_socket, request):
        self.users = [] 
        self.checkboxes = {}
        self.client_socket = client_socket
        self.parent = parent
        self.controller = controller
        self.request = request
        self.added_users = 0
        self.number = 0
        self.errors = []

        tk.Frame.__init__(self, parent)
        self.winfo_toplevel().minsize(400, 300)
        windowWidth = self.winfo_toplevel().winfo_reqwidth()
        windowHeight = self.winfo_toplevel().winfo_reqheight()

        positionRight = int(self.winfo_toplevel().winfo_screenwidth()/2 - windowWidth)
        positionDown = int(self.winfo_toplevel().winfo_screenheight()/2 - windowHeight)
        self.winfo_toplevel().geometry("+{}+{}".format(positionRight, positionDown))

        self.winfo_toplevel().title("Chat Creation Panel")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        label_details = tk.Label(self, text="Please choose the users from list:", font=LARGE_FONT)
        label_details.grid(row=0, column=0, sticky="nsew", padx=10, pady=10) 

        self.error_user_load = tk.StringVar() 
        self.error_user_add = tk.StringVar()

        self.vsb = tk.Scrollbar(self, orient="vertical")
        self.text = tk.Text(self, width=40, height=20, 
                            yscrollcommand=self.vsb.set)
        self.vsb.config(command=self.text.yview)
        self.vsb.grid(row=1, column=1, sticky="nsew", padx=2, pady=2)
        self.text.grid(row=1, column=0, sticky="nsew", padx=10, pady=10) 

        label_error_usser_load = tk.Label(self, textvariable=self.error_user_load, fg="red")
        label_error_usser_load.grid(row=2, column=0, sticky="nsew", padx=2, pady=2)

        create_button = tk.Button(self, text="Add users", width=20, height=1, command = self.add_to_chat)
        create_button.grid(row=3, column=0, sticky="nsew", padx=2, pady=2)

        label_error_user_add= tk.Label(self, textvariable=self.error_user_add, fg="red")
        label_error_user_add.grid(row=5, column=0, sticky="nsew", padx=2, pady=2)

        back_chat_panel_button = tk.Button(self, text="Back to Chat", width=20, height=1, command = self.back_to_chat)
        back_chat_panel_button.grid(row=6, column=0, sticky="nsew", padx=2, pady=2)

        back_button = tk.Button(self, text="Log out", width=20, height=1, command = self.back_to_startpage)
        back_button.grid(row=7, column=0, sticky="nsew", padx=2, pady=2)

    def get_users(self):
        self.request.get_users()
        self.client_socket.send_message(self.request.get_prepared_request())

    def fill_users(self):
        self.text.configure(state='normal')
        self.text.delete("1.0",tk.END)
        self.text.configure(state='disabled')
        self.checkboxes = {}
        for u in self.users:
            if u != self.controller.client_socket.get_client_name():
                cv = tk.IntVar()
                cb = tk.Checkbutton(self, text="", variable=cv, onvalue=1, offvalue=0, width=2, height=1)
                self.checkboxes[u] = cv
                self.text.configure(state='normal')
                self.text.window_create("end", window=cb, padx=0, pady=0, align="bottom")
                self.text.insert("end", " "+u+"\n") 
                self.text.configure(state='disabled')

    def clean_errors(self):
        self.error_user_load.set("")
        self.error_user_add.set("")
    
    def clean_everything(self):
        self.fill_users()
        self.clean_errors()

    def back_to_chat(self):
        self.controller.show_frame("ChatPage")
        self.clean_everything()

    def back_to_startpage(self):
        self.controller.show_frame("WelcomePage")
        self.clean_everything()

    def add_to_chat(self):
        checks = [ i.get() for i in self.checkboxes.values()]
        if 1 in checks:
            for u, c in self.checkboxes.items():
                if c.get() == 1:
                    self.request.add_to_chat(u, self.controller.chat_id)
                    self.client_socket.send_message(self.request.get_prepared_request())
                    self.number += 1
        else:
            self.error_user_add.set("You have to choose at least one member!")

    def message_arrived(self, message):
        msg = message["msg"]
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
        elif message["action"] == "add_to_chat":
            if message["succeed"] == True:
                self.clean_errors()
                self.added_users += 1
                self.error_user_add.set("User added")
            else:
                self.clean_errors()
                self.error_user_add.set(message["msg"])

    def set_title_frame(self):
        self.winfo_toplevel().title("Add User Panel")