from tkinter import *
from tkinter import messagebox
from datetime import datetime


class CashierScreen:
    def __init__(self, sock, username):
        self.sock = sock
        self.username = username
        self.items = []   # list of all items

        self.win = Tk()
        self.win.title("Cashier Panel of" + username)

        Label(self.win, text="Book ID:").grid(row=0, column=0, padx=5, pady=5, sticky=E)
        self.bookid_entry = Entry(self.win)
        self.bookid_entry.grid(row=0, column=1, padx=5, pady=5)

        Label(self.win, text="Quantity:").grid(row=1, column=0, padx=5, pady=5, sticky=E)
        self.qty_entry = Entry(self.win)
        self.qty_entry.grid(row=1, column=1, padx=5, pady=5)

        # add book section
        self.add_btn = Button(self.win, text="Add book", command=self.add_item)
        self.add_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        Label(self.win, text="Books in transaction:").grid(row=3, column=0, columnspan=2)
        self.listbox = Listbox(self.win, width=50)
        self.listbox.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # optional discount code section
        Label(self.win, text="Discount code (optional):").grid(row=5, column=0, padx=5, pady=5, sticky=E)
        self.discount_entry = Entry(self.win)
        self.discount_entry.grid(row=5, column=1, padx=5, pady=5)

        # transaction clearing closing buttons
        self.create_btn = Button(self.win, text="Create Transaction", command=self.create_transaction)
        self.create_btn.grid(row=6, column=0, padx=5, pady=10)

        self.clear_btn = Button(self.win, text="Clear", command=self.clear_all)
        self.clear_btn.grid(row=6, column=1, padx=5, pady=10)

        self.close_btn = Button(self.win, text="Close", command=self.close_cashier)
        self.close_btn.grid(row=7, column=0, columnspan=2, pady=10)

        # close window
        self.win.protocol("WM_DELETE_WINDOW", self.close_cashier)
        self.win.mainloop()

    def add_item(self):
        bookid = self.bookid_entry.get().strip()
        q_str = self.qty_entry.get().strip()

        # check if empty
        if bookid == "" or q_str == "":
            messagebox.showerror("Error", "Enter book id and quantity.")
            return

        try:
            q = int(q_str)
        except:
            messagebox.showerror("Error", "Quantity must be integer.")
            return

        if q <= 0:
            messagebox.showerror("Error", "Quantity must be positive.")
            return


        self.items.append((bookid, q))
        self.listbox.insert(END, "Book " + bookid + " x " + str(q))

        # entry cleaning
        self.bookid_entry.delete(0, END)
        self.qty_entry.delete(0, END)

    def clear_all(self):
        # reset for next trasactiosn
        self.items = []
        self.listbox.delete(0, END)
        self.discount_entry.delete(0, END)

    def create_transaction(self):
        #  empty check
        if len(self.items) == 0:
            messagebox.showerror("Error", "No books added.")
            return

        # use current time as stting
        dt_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        disc = self.discount_entry.get().strip()

        # build the message for server
        parts = ["transaction", dt_str, disc, self.username]
        for (bid, q) in self.items:
            parts.append(bid + "-" + str(q))
        msg = ";".join(parts)

        try:
            self.sock.send(msg.encode())
            ans = self.sock.recv(4096).decode().strip()
        except:
            messagebox.showerror("Error", "Connection error.")
            return

        # server confirmation or failiure
        if ans.startswith("transactionconfirmation;"):
            tmp = ans.split(";", 1)
            total = tmp[1] if len(tmp) > 1 else ""
            messagebox.showinfo("Transaction", "Succes. Total price: " + total)
            self.clear_all()
        elif ans.startswith("transactionfailure;"):
            tmp = ans.split(";", 1)
            reason = tmp[1] if len(tmp) > 1 else "unknown"
            messagebox.showerror("Transaction", reason)
        else:
            # that section meens some kind of server error
            messagebox.showerror("Error", "Unknown response: " + ans)

    def close_cashier(self):
        # try to tell server cashier is closing
        try:
            self.sock.send("closeconnection".encode())
        except:
            pass
        try:
            self.sock.close()
        except:
            pass
        self.win.destroy()
