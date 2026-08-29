import socket
import tkinter as tk
from tkinter import messagebox, simpledialog
from manager import ManagerPanel
from cashier import CashierScreen

class LoginWindow:
    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()
        self.root.title("Bookstore Login")
        
        self.root.geometry("300x200")
        
        self.root.eval('tk::PlaceWindow . center')
        
        self.create_widgets()
    
    def create_widgets(self):
        title_label = tk.Label(self.root, text="Bookstore Login")
        title_label.pack(pady=10)
        
        
        username_frame = tk.Frame(self.root)
        username_frame.pack(pady=5)
        tk.Label(username_frame, text="Username:", width=10).pack(side=tk.LEFT)
        self.username_entry = tk.Entry(username_frame)
        self.username_entry.pack(side=tk.LEFT)
        self.username_entry.focus()
        
        
        password_frame = tk.Frame(self.root)
        password_frame.pack(pady=5)
        tk.Label(password_frame, text="Password:", width=10).pack(side=tk.LEFT)
        self.password_entry = tk.Entry(password_frame, show="*")
        self.password_entry.pack(side=tk.LEFT)
        
        
        login_button = tk.Button(self.root, text="Login", command=self.attempt_login, width=15)
        login_button.pack(pady=20)
        
       
        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack()
        
      
        self.root.bind('<Return>', lambda event: self.attempt_login())

    def attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.status_label.config(text="Please enter both username and password.")
            return

        success = self.client.login(username, password)
        if success:
            messagebox.showinfo("Login Successful", f"Welcome {self.client.username}!")
            self.root.destroy()
            self.open_user_panel()
        else:
            self.status_label.config(text="Invalid username or password")

    def open_user_panel(self):
        if self.client.role == "Cashier":
            CashierScreen(self.client.client_socket, self.client.username)
        elif self.client.role == "Manager":
             ManagerPanel(self.client)
        else:
            messagebox.showerror("Error", "Unknown user role.")

        
    def run(self):
        self.root.mainloop()