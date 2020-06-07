import tkinter as tk

class WelcomePage(tk.Frame):

    def __init__(self, parent, controller, client_socket, request):
        self.client_socket = client_socket
        self.parent = parent
        self.controller = controller
        self.request = request

        tk.Frame.__init__(self,parent)
        self.winfo_toplevel().minsize(300, 200)
        windowWidth = self.winfo_toplevel().winfo_reqwidth()
        windowHeight = self.winfo_toplevel().winfo_reqheight()

        self.winfo_toplevel().geometry('400x500+400+300')
        self.winfo_toplevel().title("Start Page")

        label_welcome = tk.Label(self, text="Welcome to chat", font=("Times New Roman", 22))
        label_welcome.pack(pady=10, padx=10)
        label_message = tk.Label(self, text="Log in to start chatting", font=("Times New Roman", 16))
        label_message.pack(pady=10, padx=10)
        
        self.username_verify = tk.StringVar()
        self.password_verify = tk.StringVar()
        self.error_username_verify = tk.StringVar()
        self.error_password_verify = tk.StringVar()
        
        label_username = tk.Label(self, text="Username", font=("Times New Roman", 14))
        label_username.pack()

        entry_username_login = tk.Entry(self, textvariable=self.username_verify, font=("Times New Roman", 14))
        entry_username_login.pack()

        label_error_username = tk.Label(self, textvariable=self.error_username_verify, fg="red", font=("Times New Roman", 14))
        label_error_username.pack()

        label_password = tk.Label(self, text="Password", font=("Times New Roman", 14))
        label_password.pack()

        entry_password_login = tk.Entry(self, textvariable=self.password_verify, show= '*', font=("Times New Roman", 14))
        entry_password_login.pack()

        label_error_password = tk.Label(self, textvariable=self.error_password_verify, fg="red", font=("Times New Roman", 14))
        label_error_password.pack()

        login_button = tk.Button(self, text="Login", command = self.login, width=12, height=2, borderwidth=2, font=("Times New Roman", 14))
        login_button.pack(pady=10, padx=10)
    
        label_do_not_have_an_account = tk.Label(self, text="You don't have an account? Register here!", font=("Times New Roman", 16))
        label_do_not_have_an_account.pack(pady=10, padx=10)

        register_button = tk.Button(self, text="Register", command=self.register, width=12, height=2, borderwidth=2, font=("Times New Roman", 14))
        register_button.pack(pady=10, padx=10)

    def login(self):
        validation_result = self.login_validation()
        result = list(filter(lambda x: x is True, validation_result))
        if len(result) == len(validation_result):
            self.request.login(self.username_verify.get(), self.password_verify.get())
            self.client_socket.send_message(self.request.get_prepared_request())

    def login_validation(self):
        positive_validation = [True, True]
        if len(self.username_verify.get()) == 0:
            self.error_username_verify.set("Username cannot be empty")
            positive_validation[0] = False
        else:
            self.error_username_verify.set("")
            positive_validation[0] = True
        if len(self.password_verify.get()) == 0:
            self.error_password_verify.set("Password cannot be empty")
            positive_validation[1] = False
        else:
            self.error_password_verify.set("")
            positive_validation[1] = True
        return positive_validation


    def register(self):
        self.clean_everything()
        self.controller.show_frame("RegisterPage")

    def message_arrived(self, message):
        if message["action"] == "logout" and message["msg"] == "Logout completed - timeout is reached":
            self.back_to_startpage()
        if message["succeed"] == True:
            self.controller.client_socket.set_client_name(self.username_verify.get())
            self.username_verify.set("")
            self.password_verify.set("")
            self.error_username_verify.set("")
            self.error_password_verify.set("")
            if message["action"] != "logout":
                self.controller.show_frame("ChatPanel")
            else:
                self.controller.show_frame("WelcomePage")

        else:
            msg = message["msg"]
            if "user" in msg:
                self.error_username_verify.set(msg)
                self.error_password_verify.set("")
            elif "password" in msg:
                self.error_password_verify.set(msg)
                self.error_username_verify.set("")
            else:
                self.error_password_verify.set(msg)
                self.error_username_verify.set("")

    def clean_everything(self):
        self.username_verify.set("")
        self.password_verify.set("")
        self.error_username_verify.set("")
        self.error_password_verify.set("")

    def set_error_labels(self, msg_one, msg_two):
        self.error_username_verify.set(msg_one)
        self.error_password_verify.set(msg_two)

    def set_title_frame(self):
        self.winfo_toplevel().title("Start Page")