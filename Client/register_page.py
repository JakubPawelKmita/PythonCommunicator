import tkinter as tk

class RegisterPage(tk.Frame):

    def __init__(self, parent, controller, client_socket, request):
        self.client_socket = client_socket
        self.parent = parent
        self.controller = controller
        self.request = request

        tk.Frame.__init__(self, parent)
        self.winfo_toplevel().minsize(400, 300)
        windowWidth = self.winfo_toplevel().winfo_reqwidth()
        windowHeight = self.winfo_toplevel().winfo_reqheight()

        self.winfo_toplevel().title("Registration Page")

        label_details = tk.Label(self, text="Please enter details below", font=("Times New Roman", 16))
        label_details.pack(pady=10, padx=10)
        
        self.username_verify = tk.StringVar()
        self.password_verify = tk.StringVar()
        self.email_verify = tk.StringVar()
        self.error_username_verify = tk.StringVar()
        self.error_password_verify = tk.StringVar()
        self.error_email_verify = tk.StringVar()
        self.error_regulations = tk.StringVar()
        self.error_registration = tk.StringVar()
        
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

        label_email = tk.Label(self, text="Email", font=("Times New Roman", 14))
        label_email.pack()

        entry_email_login = tk.Entry(self, textvariable=self.email_verify, font=("Times New Roman", 14))
        entry_email_login.pack()

        label_error_email = tk.Label(self, textvariable=self.error_email_verify, fg="red", font=("Times New Roman", 14))
        label_error_email.pack()

        self.check_variable = tk.IntVar()
        check_button_regulations = tk.Checkbutton(self, text="I've read the chat regulations", variable=self.check_variable, onvalue=1, offvalue=0, font=("Times New Roman", 14))
        check_button_regulations.pack()
        label_error_regulations = tk.Label(self, textvariable=self.error_regulations, fg="red", font=("Times New Roman", 14), )
        label_error_regulations.pack()

        register_button = tk.Button(self, text="Register", width=12, height=2, command = self.register, font=("Times New Roman", 14))
        register_button.pack(pady=10, padx=10)

        label_error_registration = tk.Label(self, textvariable=self.error_registration, fg="green", font=("Times New Roman", 14))
        label_error_registration.pack()

        back_button = tk.Button(self, text="Back to Login Page", width=20, height=2, command = self.back_to_startpage, font=("Times New Roman", 14))
        back_button.pack(pady=10, padx=10)

    def register(self):
        validation_result = self.register_validation()
        result = list(filter(lambda x: x is True, validation_result))
        if len(result) == len(validation_result):
            self.request.register(self.username_verify.get(), self.password_verify.get(), self.email_verify.get())
            self.client_socket.send_message(self.request.get_prepared_request())

    def register_validation(self):
        positive_validation = [True, True, True, True]
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
        if len(self.email_verify.get()) == 0:
            self.error_email_verify.set("Email cannot be empty")
            positive_validation[2] = False
        else:
            self.error_email_verify.set("")
            positive_validation[2] = True
        if self.check_variable.get() == 0:
            self.error_regulations.set("You have to agree with the rules")
            positive_validation[3] = False
        else:
            self.error_regulations.set("")
            positive_validation[3] = True
        return positive_validation
        
    def back_to_startpage(self):
        self.clean_everything()
        self.check_variable.set(0)
        self.controller.show_frame("WelcomePage")

    def message_arrived(self, message):
        if message["succeed"] == True:
            self.error_registration.set("Congratulations! Now you can log in")
            self.error_username_verify.set("")
            self.error_password_verify.set("")
            self.error_email_verify.set("")
        else:
            msg = message["msg"]
            if "user" in msg:
                self.error_username_verify.set(msg)
                self.error_password_verify.set("")
                self.error_email_verify.set("")
            elif "password" in msg:
                self.error_password_verify.set(msg)
                self.error_username_verify.set("")
                self.error_email_verify.set("")
            elif "email" in msg:
                self.error_email_verify.set(msg)
                self.error_password_verify.set("")
                self.error_username_verify.set("")
        
    def clean_everything(self):
        self.username_verify.set("")
        self.password_verify.set("")
        self.email_verify.set("")
        self.set_error_labels("","","","","")

    def set_error_labels(self, msg_one, msg_two, msg_three, msg_four, msg_five):
        self.error_username_verify.set(msg_one)
        self.error_password_verify.set(msg_two)
        self.error_email_verify.set(msg_three)
        self.error_regulations.set(msg_four)
        self.error_registration.set(msg_five)
    
    def set_title_frame(self):
        self.winfo_toplevel().title("Registration Page")