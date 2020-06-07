import tkinter as tk
from tkinter import messagebox as mb

LARGE_FONT= ("Verdana", 12)

class MembersPage(tk.Frame):

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

        self.winfo_toplevel().title("Members Panel")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        label_details = tk.Label(self, text="Chatmembers are listed below:", font=("Times New Roman", 16))
        label_details.grid(row=0, column=0, sticky="nsew", padx=10, pady=10) 

        self.error_user_load = tk.StringVar() 

        self.vsb = tk.Scrollbar(self, orient="vertical")
        self.text = tk.Text(self, width=40, height=20, 
                            yscrollcommand=self.vsb.set)
        self.vsb.config(command=self.text.yview)
        self.vsb.grid(row=1, column=1, sticky="nsew", padx=2, pady=2)
        self.text.grid(row=1, column=0, sticky="nsew", padx=10, pady=10) 

        label_error_user_load = tk.Label(self, textvariable=self.error_user_load, fg="red")
        label_error_user_load.grid(row=2, column=0, sticky="nsew", padx=2, pady=2)

        back_chat_panel_button = tk.Button(self, text="Back to Chat", width=20, height=2, command = self.back_to_chat, font=("Times New Roman", 14))
        back_chat_panel_button.grid(row=6, column=0, sticky="nsew", columnspan=2, padx=2, pady=2)

        back_button = tk.Button(self, text="Log out", width=20, height=2, command=self.logout, font=("Times New Roman", 14))
        back_button.grid(row=7, column=0, sticky="nsew", columnspan=2, padx=2, pady=2)

    def get_users(self):
        self.request.get_chat_members(self.controller.chat_id)
        self.client_socket.send_message(self.request.get_prepared_request())

    def fill_users(self):
        self.text.configure(state='normal')
        self.text.delete("1.0",tk.END)
        self.text.configure(state='disabled')
        for i,u in enumerate(self.users):
            self.text.configure(state='normal')
            self.text.insert("end", str(i+1)+". "+u+"\n") 
            self.text.configure(state='disabled')
    
    def clean_everything(self):
        self.fill_users()
        self.error_user_load.set("")

    def back_to_chat(self):
        self.controller.show_frame("ChatPage")
        self.clean_everything()

    def back_to_startpage(self):
        self.controller.show_frame("WelcomePage")
        self.clean_everything()

    def logout(self):
        self.request.logout()
        self.client_socket.send_message(self.request.get_prepared_request())
        self.back_to_startpage()

    def show_timeout_message(self):
        mb.showerror("Logout", "Logout completed - timeout is reached")

    def message_arrived(self, message):
        msg = message["msg"]
        if message["action"] == "logout" and message["msg"] == "Logout completed - timeout is reached":
            self.show_timeout_message()
            self.back_to_startpage()
        if message["action"] == "get_chat_members":
            if message["succeed"] == True and message['members'] is not None:
                self.users = message['members']
                self.fill_users()
                self.error_user_load.set("")
            else:
                self.error_user_load.set(msg)

    def set_title_frame(self):
        self.winfo_toplevel().title("Add User Panel")