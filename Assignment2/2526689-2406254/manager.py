import socket
import tkinter as tk
from tkinter import messagebox, simpledialog


class ManagerPanel:
    def __init__(self, client):
        self.client = client
        self.create_gui()

    def create_gui(self):
        self.window = tk.Tk()
        self.window.title("Inventory Management")
        self.window.geometry("500x500")

        self.create_widgets()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    def create_widgets(self):
        title_label = tk.Label(self.window, text="Inventory Management")
        title_label.pack(pady=10)

        add_book_button = tk.Button(self.window, text="Add Book", command=self.add_book)
        add_book_button.pack(pady=5)

        update_stock_button = tk.Button(self.window, text="Update", command=self.update_inventory)
        update_stock_button.pack(pady=5)

        report_frame = tk.LabelFrame(self.window, text="Reports", padx=10, pady=10)
        report_frame.pack(pady=10, padx=20, fill="x")

        report1_button = tk.Button(report_frame, text="Top-Selling Author", command=lambda: self.generate_report(1),
                                   width=20)
        report1_button.pack(pady=5)

        report2_button = tk.Button(report_frame, text="Most Profitable Genre", command=lambda: self.generate_report(2),
                                   width=20)
        report2_button.pack(pady=5)

        report3_button = tk.Button(report_frame, text="Busiest Cashier", command=lambda: self.generate_report(3),
                                   width=20)
        report3_button.pack(pady=5)

        close_button = tk.Button(self.window, text="Close", command=self.on_closing, width=15)
        close_button.pack(pady=20)

    def add_book(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("Add New Book")
        dialog.geometry("400x350")
        dialog.transient(self.window)
        dialog.grab_set()

        fields = []
        labels = ["Book ID:", "Title:", "Author(s):", "Genre:", "Price:", "Quantity:"]
        entries = []

        for i, label in enumerate(labels):
            tk.Label(dialog, text=label, width=12).grid(row=i, column=0, pady=8, padx=5)
            entry = tk.Entry(dialog, width=30)
            entry.grid(row=i, column=1, pady=8, padx=5)
            entries.append(entry)

        status_label = tk.Label(dialog, text="")
        status_label.grid(row=len(labels), column=0, columnspan=2, pady=10)

        def submit():
            values = [entry.get().strip() for entry in entries]

            for i, value in enumerate(values):
                if not value:
                    status_label.config(text=f"Please fill in {labels[i]}")
                    return

            try:
                book_id = values[0]
                title = values[1]
                author = values[2]
                genre = values[3]
                price = float(values[4])
                quantity = int(values[5])

                if price <= 0 or quantity < 0:
                    status_label.config(text="Price must be > 0, Quantity >= 0")
                    return

                success, message = self.client.add_book(book_id, title, author, genre, price, quantity)

                if success:
                    messagebox.showinfo("Success", message)
                    dialog.destroy()
                else:
                    status_label.config(text=message)

            except ValueError:
                status_label.config(text="Invalid price or quantity format")

        button_frame = tk.Frame(dialog)
        button_frame.grid(row=len(labels) + 1, column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Add Book", command=submit,
                  width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                  width=12).pack(side=tk.LEFT, padx=5)

        entries[0].focus()

    def update_inventory(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("Update Book Quantity")
        dialog.geometry("300x200")
        dialog.transient(self.window)
        dialog.grab_set()

        tk.Label(dialog, text="Book ID:", width=10).grid(row=0, column=0, pady=15, padx=5)
        book_id_entry = tk.Entry(dialog, width=25)
        book_id_entry.grid(row=0, column=1, pady=15, padx=5)

        tk.Label(dialog, text="New Quantity:", width=10).grid(row=1, column=0, pady=15, padx=5)
        quantity_entry = tk.Entry(dialog, width=25)
        quantity_entry.grid(row=1, column=1, pady=15, padx=5)

        status_label = tk.Label(dialog, text="")
        status_label.grid(row=2, column=0, columnspan=2, pady=10)

        def submit():
            book_id = book_id_entry.get().strip()
            quantity_str = quantity_entry.get().strip()

            if not book_id or not quantity_str:
                status_label.config(text="Please fill in all fields")
                return

            try:
                quantity = int(quantity_str)
                if quantity < 0:
                    status_label.config(text="Quantity must be >= 0")
                    return

                success, message = self.client.update_quantity(book_id, quantity)

                if success:
                    messagebox.showinfo("Success", message)
                    dialog.destroy()
                else:
                    status_label.config(text=message)

            except ValueError:
                status_label.config(text="Invalid quantity format")

        button_frame = tk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=15)

        tk.Button(button_frame, text="Update", command=submit,
                  width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                  width=12).pack(side=tk.LEFT, padx=5)

        book_id_entry.focus()

    def generate_report(self, report_number):
        report_names = {
            1: "Top-Selling Author",
            2: "Most Profitable Genre",
            3: "Busiest Cashier"
        }

        success, response = self.client.generate_report(report_number)
        if success:
            parts = response.split(';')
            report_type = parts[0]

            if report_type == f"report{report_number}":
                if len(parts) >= 3:
                    if report_number == 1:
                        message = f"{report_names[report_number]}:\n\nAuthor: {parts[1]}\nBooks Sold: {parts[2]}"
                    elif report_number == 2:
                        message = f"{report_names[report_number]}:\n\nGenre: {parts[1]}\nRevenue: ${parts[2]}"
                    elif report_number == 3:
                        message = f"{report_names[report_number]}:\n\nCashier: {parts[1]}\nTransactions: {parts[2]}"
                    else:
                        message = response
                else:
                    message = parts[1] if len(parts) > 1 else response

                messagebox.showinfo(f"Report {report_number}", message)
            else:
                messagebox.showerror("Error", f"Unexpected response: {response}")
        else:
            messagebox.showerror("Error", f"Failed to generate report: {response}")

    def on_closing(self):
        if messagebox.askyesno("Quit", "Are you sure you want to close?"):
            self.client.close_connection()
            self.window.destroy()