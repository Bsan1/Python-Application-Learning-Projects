import socket
import tkinter as tk
from tkinter import messagebox, simpledialog
import threading
from login import LoginWindow

class BookstoreClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None
        self.username = None
        self.role = None
        self.connected = False
        self.login_window = None

    #Conect to server
    def connect(self):
        try: 
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            
            # Wait for connection success message
            response = self.client_socket.recv(1024).decode()
            if response == "connectionsuccess":
                self.connected = True
                print("Connected to server successfully.")
                return True
            else:
                print("Failed to connect to server.")
                return False
        
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    # Send message to server and receive response
    def send_message(self, message):
        if self.connected:
            self.client_socket.send(message.encode())
            response = self.client_socket.recv(1024).decode()
            return response
        else:
            print("Not connected to server.")
            return None
    
    # Login 
    def login(self, username, password):
        message = f"login;{username};{password}"
        response = self.send_message(message)

        if response and response.startswith("loginsuccess"):
            parts = response.split(";")
            self.username = parts[1]
            self.role = parts[2]
            print(f"Login successful as {self.username} ({self.role})")
            return True
        else:
            print("Login failed.")
            return False
    
     # Add a new book to inventory
    def add_book(self, book_id, title, author, genre, price, quantity):
        try:
            message = f"addbook;{book_id};{title};{author};{genre};{price};{quantity}"
            response = self.send_message(message)
            
            if response == "addbookconfirmation":
                return True, "Book added successfully"
            elif response.startswith("error"):
                parts = response.split(';')
                error_msg = parts[1] if len(parts) > 1 else "Error adding book"
                return False, error_msg
            else:
                return False, f"Unexpected response: {response}"
                
        except Exception as e:
            return False, str(e)
    
    # Update book quantity
    def update_quantity(self, book_id, quantity):
        try:
            message = f"updatequantity;{book_id};{quantity}"
            response = self.send_message(message)
            
            if response == "updatequantityconfirmation":
                return True, "Quantity updated successfully"
            elif response.startswith("error"):
                parts = response.split(';')
                error_msg = parts[1] if len(parts) > 1 else "Error updating quantity"
                return False, error_msg
            else:
                return False, f"Unexpected response: {response}"
                
        except Exception as e:
            return False, str(e)
    
    # Generate reports
    def generate_report(self, report_number):
        try:
            message = f"report{report_number}"
            response = self.send_message(message)
            
            if response:
                return True, response
            else:
                return False, "No response from server"
                
        except Exception as e:
            return False, str(e)
    
        
    def close_connection(self):
        if self.connected:
            self.send_message("logout")
            self.client_socket.close()
            self.connected = False
            print("Connection closed.")
    
    def start_gui(self):
        self.login_window = LoginWindow(self)
        self.login_window.run()



host = "127.0.0.1"
port = 5000

client = BookstoreClient(host, port)
if client.connect():
    client.start_gui()


