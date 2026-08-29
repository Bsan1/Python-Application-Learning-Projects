import socket


# threads implemented
def read_users():
    users = {}
    try:
        f = open("users.txt", "r", encoding="utf-8")
    except FileNotFoundError:
        return users

    for line in f:
        line = line.strip()
        if line == "":
            continue
        parts = line.split(";")
        if len(parts) != 3:
            # ignore broken lines
            continue
        username = parts[0]
        password = parts[1]
        role = parts[2]
        users[username] = (password, role)
    f.close()
    return users


def read_inventory():
    inv = {}
    try:
        f = open("inventory.txt", "r", encoding="utf-8")
    except FileNotFoundError:
        return inv

    for line in f:
        line = line.strip()
        if not line:
            continue
        pieces = line.split(";")
        if len(pieces) != 6:
            continue
        bookid, title, authors, genre, price_str, qty_str = pieces
        try:
            price = float(price_str)
            qty = int(qty_str)
        except:
            # malformatted line skip
            continue
        inv[bookid] = [title, authors, genre, price, qty]
    f.close()
    return inv


def write_inventory(inv):
    try:
        f = open("inventory.txt", "w", encoding="utf-8")
    except:
        return

    # inv fortmatted writing
    keys = list(inv.keys())
    keys.sort()
    for k in keys:
        title, authors, genre, price, qty = inv[k]
        line = str(k) + ";" + title + ";" + authors + ";" + genre + ";" + ("%.2f" % price) + ";" + str(qty) + "\n"
        f.write(line)
    f.close()


def read_discount_codes():
    codes = []
    try:
        f = open("discountcodes.txt", "r", encoding="utf-8")
    except FileNotFoundError:
        return codes

    for line in f:
        code = line.strip()
        if code != "":
            codes.append(code)
    f.close()
    return codes


def write_discount_codes(codes):
    try:
        f = open("discountcodes.txt", "w", encoding="utf-8")
    except:
        return

    for c in codes:
        f.write(c + "\n")
    f.close()


# cashier transaction is herr process
def append_transaction(cashier, dt_str, discount_flag, total_price, items):
    try:
        f = open("transactions.txt", "a", encoding="utf-8")
    except:
        return

    line = cashier + ";" + dt_str + ";" + discount_flag + ";" + ("%.2f" % total_price)
    if len(items) > 0:
        line = line + ";" + ";".join(items)
    line += "\n"
    f.write(line)
    f.close()


def handle_login(sock, msg):
    # takeing login info
    parts = msg.split(";")
    if len(parts) != 3:
        sock.send("loginfailure".encode())
        return None, None

    username = parts[1]
    password = parts[2]

    users = read_users()
    if username in users and users[username][0] == password:
        role = users[username][1]
        reply = "loginsuccess;" + username + ";" + role
        sock.send(reply.encode())
        return username, role
    else:
        sock.send("loginfail".encode())
        return None, None


def handle_transaction(sock, msg):
    # handle upcoming transaction based on socket and correctly formetted message
    parts = msg.split(";")
    if len(parts) < 5:
        sock.send("transactionfailure;transaction format is wrong.".encode())
        return

    datetime_str = parts[1]
    discount_code = parts[2]
    cashier = parts[3]
    item_parts = parts[4:]

    items = []
    for it in item_parts:
        it = it.strip()
        if it == "":
            continue
        temp = it.split("-")
        if len(temp) != 2:
            sock.send("transactionfailure;item format is wrong.".encode())
            return
        bookid = temp[0]
        qty_str = temp[1]
        try:
            qty = int(qty_str)
        except:
            sock.send("transactionfailure;quantity type is not an int.".encode())
            return
        if qty <= 0:
            sock.send("transactionfailure;quantity is not positive.".encode())
            return
        items.append((bookid, qty))

    if len(items) == 0:
        sock.send("transactionfailure;no books in the transaction.".encode())
        return

    inv = read_inventory()
    if inv == {}:
        sock.send("transactionfailure;nnventory is not workng.".encode())
        return

    total_gross = 0.0
    error_reason = ""

    for (bookid, qty) in items:
        if bookid not in inv:
            error_reason = "book " + bookid + " is not found."
            break
        title, authors, genre, price, stock = inv[bookid]
        if stock < qty:
            error_reason = "no stock on '" + title + "' (ID " + bookid + ")."
            break
        total_gross = total_gross + price * qty

    if error_reason != "":
        sock.send(("transactionfailure;" + error_reason).encode())
        return

    discount_flag = "N"
    total_price = total_gross
    codes = read_discount_codes()

    if discount_code != "":
        if discount_code in codes:
            discount_flag = "Y"
            total_price = round(total_gross * 0.90, 2)  # 10%
            # remove firs
            new_codes = []
            removed = False
            for c in codes:
                if c == discount_code and not removed:
                    removed = True
                else:
                    new_codes.append(c)
            write_discount_codes(new_codes)
        else:
            sock.send("transactionfailure;discount code is worng or used.".encode())
            return

    # update inv
    for (bookid, qty) in items:
        title, authors, genre, price, stock = inv[bookid]
        inv[bookid][4] = stock - qty

    write_inventory(inv)

    item_strs = []
    for (bookid, qty) in items:
        item_strs.append(bookid + "-" + str(qty))

    append_transaction(cashier, datetime_str, discount_flag, total_price, item_strs)

    ans = "transactionconfirmation;" + ("%.2f" % total_price)
    sock.send(ans.encode())


def handle_add_book(sock, msg):
    # message format addbook;bookid;title;authors;genre;price;qty
    parts = msg.split(";")
    if len(parts) != 7:
        sock.send("addbookconfirmation".encode())
        return

    bookid = parts[1]
    title = parts[2]
    authors = parts[3]
    genre = parts[4]
    price_str = parts[5]
    qty_str = parts[6]

    # price and quantity format check
    try:
        price = float(price_str)
        qty = int(qty_str)
    except:
        sock.send("addbookconfirmation".encode())
        return

    inv = read_inventory()
    inv[bookid] = [title, authors, genre, price, qty]
    write_inventory(inv)

    sock.send("addbookconfirmation".encode())


def handle_update_quantity(sock, msg):
    # message format updatequantity;bookid;quantity

    parts = msg.split(";")
    if len(parts) != 3:
        sock.send("updatequantityconfirmation".encode())
        return

    bookid = parts[1]
    qty_str = parts[2]

    # quantity format check
    try:
        amount = int(qty_str)
    except:
        sock.send("updatequantityconfirmation".encode())
        return

    # adds amount to bookid in inventoryt
    inv = read_inventory()
    if bookid in inv:
        inv[bookid][4] = inv[bookid][4] + amount
        write_inventory(inv)

    sock.send("updatequantityconfirmation".encode())


def report_top_selling_author():
    inv = read_inventory()
    author_counts = {}

    try:
        f = open("transactions.txt", "r", encoding="utf-8")
    except FileNotFoundError:
        f = None

    if f is not None:
        for line in f:
            line = line.strip()
            if line == "":
                continue
            parts = line.split(";")
            if len(parts) < 5:
                continue
            item_parts = parts[4:]
            for it in item_parts:
                if it == "":
                    continue
                try:
                    bookid, qty_str = it.split("-")
                    qty = int(qty_str)
                except:
                    continue
                if bookid not in inv:
                    continue
                title, authors, genre, price, stock = inv[bookid]
                auth_list = authors.split("and")
                for a in auth_list:
                    a = a.strip()
                    if a == "":
                        continue
                    if a not in author_counts:
                        author_counts[a] = qty
                    else:
                        author_counts[a] = author_counts[a] + qty
        f.close()

    if author_counts == {}:
        return "no sale data is avaiable."

    max_val = max(author_counts.values())
    result = []
    for a in author_counts:
        if author_counts[a] == max_val:
            result.append(a)
    return result


def report_most_profitable_genre():
    inv = read_inventory()
    genre_revenue = {}

    try:
        f = open("transactions.txt", "r", encoding="utf-8")
    except FileNotFoundError:
        f = None

    if f is not None:
        for line in f:
            line = line.strip()
            if line == "":
                continue
            parts = line.split(";")
            if len(parts) < 5:
                continue
            item_parts = parts[4:]
            for it in item_parts:
                if it == "":
                    continue
                try:
                    bookid, qty_str = it.split("-")
                    qty = int(qty_str)
                except:
                    continue
                if bookid not in inv:
                    continue
                title, authors, genre, price, stock = inv[bookid]
                revenue = price * qty
                if genre not in genre_revenue:
                    genre_revenue[genre] = revenue
                else:
                    genre_revenue[genre] = genre_revenue[genre] + revenue
        f.close()

    if genre_revenue == {}:
        return "no sale data is avaiable."

    max_rev = max(genre_revenue.values())
    result = []
    for g in genre_revenue:
        if genre_revenue[g] == max_rev:
            result.append(g)
    return result


def report_busiest_cashier():
    cashier_counts = {}

    try:
        f = open("transactions.txt", "r", encoding="utf-8")
    except FileNotFoundError:
        f = None

    if f is not None:
        for line in f:
            line = line.strip()
            if line == "":
                continue
            parts = line.split(";")
            if len(parts) < 5:
                continue
            cashier = parts[0]
            if cashier not in cashier_counts:
                cashier_counts[cashier] = 1
            else:
                cashier_counts[cashier] = cashier_counts[cashier] + 1
        f.close()

    if cashier_counts == {}:
        return "no sale data is avaiable."

    max_val = max(cashier_counts.values())
    result = []
    for c in cashier_counts:
        if cashier_counts[c] == max_val:
            result.append(c)
    return result


def handle_report(sock, msg):
    if msg == "report1":
        r = report_top_selling_author()
        prefix = "report1;"
    elif msg == "report2":
        r = report_most_profitable_genre()
        prefix = "report2;"
    elif msg == "report3":
        r = report_busiest_cashier()
        prefix = "report3;"
    else:
        return

    if isinstance(r, str):
        answer = prefix + r
    else:
        if len(r) == 0:
            answer = prefix + "No data."
        else:
            answer = prefix + ";".join(r)

    sock.send(answer.encode())


def handle_client(sock, addr):
    print("Client connected:", addr)
    try:
        sock.send("connectionsuccess".encode())
    except:
        sock.close()
        return

    username = None
    role = None

    # login loop
    while username is None:
        try:
            data = sock.recv(4096)
        except:
            sock.close()
            return
        if not data:
            sock.close()
            return

        msg = data.decode().strip()
        if msg == "closeconnection":
            sock.close()
            return
        if msg.startswith("login;"):
            username, role = handle_login(sock, msg)
        else:
            sock.send("loginfailure".encode())

    # after login
    while True:
        try:
            data = sock.recv(4096)
        except:
            break
        if not data:
            break

        msg = data.decode().strip()
        if msg == "closeconnection":
            break

        if msg.startswith("transaction;") and role == "Cashier":
            handle_transaction(sock, msg)
        elif msg.startswith("addbook;") and role == "Manager":
            handle_add_book(sock, msg)
        elif msg.startswith("updatequantity;") and role == "Manager":
            handle_update_quantity(sock, msg)
        elif msg.startswith("report"):
            handle_report(sock, msg)
        else:
            # ignore other messages
            pass

    sock.close()
    print("client disconnected:", addr)


def main():
    host = "127.0.0.1"
    port = 5000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print("server is started on", host, ":", port)

    while True:
        client_socket, address = s.accept()
        # as seen, no thread implemented :D
        handle_client(client_socket, address)


if __name__ == "__main__":
    main()
