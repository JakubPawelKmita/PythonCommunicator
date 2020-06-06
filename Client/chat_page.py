import tkinter as tk
from tkinter import messagebox as mb

LARGE_FONT= ("Verdana", 12)

class ChatPage(tk.Frame):

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

        self.grid(row=0, column=0, sticky="nsew")
                
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.vsb = tk.Scrollbar(self, orient="vertical")
        self.chat = tk.Text(self, yscrollcommand=self.vsb.set)
        self.vsb.config(command=self.chat.yview)
        self.vsb.grid(column=1, row=0, sticky="nsew", padx=2, pady=2)
        self.chat.configure(state='normal')
        self.chat.insert('end', '')
        self.chat.configure(state='disabled')
        self.chat.grid(column=0, row=0, sticky="nsew")

        self.textField = tk.Entry(self)
        self.textField.grid(column=0, row=1, sticky="nsew")

        self.buttonSend = tk.Button(self)
        self.buttonSend["text"] = "Send Message"
        self.buttonSend.grid(column=0, row=2, sticky="nsew")
        self.buttonSend.bind("<Button-1>", lambda event: self.sendMessageClick())

        self.buttonAddUser = tk.Button(self)
        self.buttonAddUser["text"] = "Add Member to this chat"
        self.buttonAddUser.grid(column=0, row=3, sticky="nsew")
        self.buttonAddUser.bind("<Button-1>", lambda event: self.add_member())

        back_chat_panel_button = tk.Button(self, text="Back to Chat Panel", width=20, height=1,
                                           command=self.back_to_chatpanel)
        back_chat_panel_button.grid(column=0, row=4, sticky="nsew")

        back_button = tk.Button(self, text="Log out", width=20, height=1, command=self.logout)
        back_button.grid(column=0, row=5, sticky="nsew")
 
        self.error_chats = tk.StringVar() 
        label_error_user_add= tk.Label(self, textvariable=self.error_chats, fg="red")
        label_error_user_add.grid(column=0, row=6, sticky="nsew")

    def back_to_chatpanel(self):
        self.error_chats.set("")
        self.chat.configure(state='normal')
        self.chat.delete("1.0",tk.END)
        self.chat.configure(state='disabled')
        self.controller.show_frame("ChatPanel")
        self.chat.configure(state='disabled')

    def back_to_startpage(self):
        self.error_chats.set("")
        self.chat.configure(state='normal')
        self.chat.delete("1.0",tk.END)
        self.chat.configure(state='disabled')
        self.controller.show_frame("WelcomePage")

    def add_member(self):
        self.controller.show_frame("AddUserToChat")
        
    def sendMessageClick(self):
        self.current_message = self.textField.get()
        if len(self.current_message) > 0:
            self.request.new_msg(self.controller.chat_id, self.current_message)
            self.client_socket.send_message(self.request.get_prepared_request())

    def chatUpdate(self, message):
        self.chat.configure(state='normal')
        self.chat.insert('end',message)
        self.chat.see("end")
        self.chat.configure(state='disabled')

    def logout(self):
        self.request.logout()
        self.client_socket.send_message(self.request.get_prepared_request())
        self.show_timeout_message()
        self.back_to_startpage()

    def show_timeout_message(self):
        mb.showerror("Logout", "Logout completed - timeout is reached")

    def message_arrived(self, message):
        msg = message["msg"]
        if message["action"] == "logout" and message["msg"] == "Logout completed - timeout is reached":
            self.show_timeout_message()
            self.back_to_startpage()
        if message["action"] == "get_msgs":
            if message["succeed"] == True:
                msgs = message["chat_msgs"]
                msgs.reverse()
                for u, m in msgs:
                    self.chat.configure(state='normal')
                    if u == self.controller.client_socket.get_client_name():
                        self.chat.insert('end', 'Me > '+ m + '\n')
                    else:
                        self.chat.insert('end', u  + ' > '+ m + '\n')
                    self.chat.see("end")
                    self.chat.configure(state='disabled')
            else:
                self.error_chats.set(msg)
        elif message["action"] == "new_msg":
            if message["succeed"] == True:
                self.chat.configure(state='normal')
                self.chat.insert('end', 'Me > '+ self.current_message + '\n')
                self.chat.see("end")
                self.chat.configure(state='disabled')
                self.textField.delete(0, "end")
            else:
                self.error_chats.set(msg)
        elif message["action"] == "chat_update":
            if message["login"] != self.controller.client_socket.get_client_name():
                self.chat.configure(state='normal')
                self.chat.insert('end', message["login"]  + ' > '+ msg + '\n')
                self.chat.see("end")
                self.chat.configure(state='disabled')
                self.textField.delete(0, "end")

    def set_title_frame(self):
        self.winfo_toplevel().title("{} Chat".format(self.controller.client_socket.get_client_name()))