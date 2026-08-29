# Assignment 2 — Bookstore Application (Client-Server, TCP)

**Spec:** `CNG445_Assignment2_20251.pdf`
**Topic:** Multithreading/concurrency, TCP socket network programming, Tkinter GUI — a bookstore client-server app with Cashier and Manager roles, transactions, discount codes, and manager statistics reports.

## Contents
- `2526689-2406254.zip` — original submission archive (untouched)
- `2526689-2406254/` — its extracted contents: `server.py`, `client.py`, `login.py`, `cashier.py`, `manager.py`, `users.txt`, `inventory.txt`, `discountcodes.txt`, `transactions.txt`, `readme.txt`
- `CNG445_Assignment2_20251.pdf` — assignment spec

## Why this grouping
`2526689-2406254.zip` is named after two student IDs (a pair submission — matches its `readme.txt`, which lists two authors: Barış Şan and Emmanuel Monye). Its contents — `server.py`/`client.py` (TCP sockets), `login.py`/`cashier.py`/`manager.py` (Tkinter role-based panels), and `users.txt`/`inventory.txt`/`discountcodes.txt`/`transactions.txt` with exactly the `;`-delimited schemas the spec dictates (`username;password;role`, `bookid;title;author(s);genre;price;quantity`, discount codes one per line, `cashier;datetime;discount;total;bookid-qty;...`) — are an exact match to Assignment 2's file names and requirements. This is Assignment 2.

## Static completeness assessment (not executed — no local Python interpreter)

Overall: **functionally broad coverage of the spec's screens and message protocol, but with a significant unmet core requirement (no concurrency) and several real protocol/logic bugs.**

**Implemented:**
- Login screen → role-based panel routing (Cashier/Manager), matching the `connectionsuccess` → `login;user;pass` → `loginsuccess;user;role` handshake.
- Cashier panel: add book-id/quantity rows, optional discount code, "Create Transaction" sends the `transaction;datetime;discountcode;cashier;bookid-qty;...` message and displays the server's confirmation/failure.
- Manager panel: Add Book, Update Quantity dialogs, and buttons for all three statistics reports.
- Server-side: reads/writes the four required text files, computes transaction totals from `inventory.txt`, applies the one-time 10% discount and removes the used code from `discountcodes.txt`, updates stock, appends to `transactions.txt`, and implements `report1`/`report2`/`report3`.

**Major gap — no concurrency (the assignment's core learning objective):**
- `server.py`'s `main()` loop calls `handle_client(client_socket, address)` synchronously right after `s.accept()` — there is no `threading.Thread` spawned per connection. The code even contains a self-aware comment: `# as seen, no thread implemented :D` (line 512). This means the server can only serve **one connected client at a time**; a second manager/cashier panel opened concurrently (which the spec explicitly requires — "multiple manager and cashier panels should be able to be opened at the same time") will hang at `connect()`/`recv()` until the first client disconnects.
- Consequently, the required **RLock thread synchronization** (5 grading points, explicitly called out in the spec) is entirely absent — there's nothing to synchronize because there's no concurrency. `client.py` has a stray `import threading` that is never actually used anywhere.

**Real bugs found by reading the code:**
1. **Login failure message typo:** `server.py`'s `handle_login` sends `"loginfail"` on bad credentials (line 128) instead of the spec's required `loginfailure`. Harmless here because the client only special-cases the `loginsuccess` prefix, but it's a protocol non-conformance.
2. **Silent false-positive confirmations:** `handle_add_book` and `handle_update_quantity` send `addbookconfirmation` / `updatequantityconfirmation` even when the request was malformed (wrong field count, non-numeric price/quantity) — i.e., on error they still tell the client "success" instead of a failure message. The manager UI has no way to learn the operation actually silently failed.
3. **Report payload/UI contract mismatch:** `report_top_selling_author`, `report_most_profitable_genre`, and `report_busiest_cashier` all return only the **name(s)** of the winner(s) (e.g. `["SomeAuthor"]`), never the actual count/revenue/transaction-total number. But `manager.py`'s `generate_report` unconditionally assumes `parts[1]` = name and `parts[2]` = statistic value (e.g. `f"Author: {parts[1]}\nBooks Sold: {parts[2]}"`). In the common case of a single winner, the server reply is only `report1;AuthorName` (2 parts), so the `len(parts) >= 3` check fails and the UI falls back to showing the bare name with no label/number at all — the "Books Sold"/"Revenue"/"Transactions" figures the manager is supposed to see are never actually sent by the server. In the (rarer) case of a tie between two winners, the second winner's *name* gets mistakenly displayed in the position where a *count* was expected. This affects all three report screens (35 of 100 grading points).
4. **Author-splitting bug:** `report_top_selling_author` splits multi-author strings with `authors.split("and")` (no surrounding spaces), which will incorrectly fragment any single author name that merely *contains* the substring "and" (e.g. "Fernando", "Alexander", "Andy Weir" would all be mis-split). The spec explicitly warns "you must ensure your code handles the white-space characters correctly when generating reports" — this is exactly that failure mode, just not triggered by the specific sample `inventory.txt` shipped with this submission (none of its author names happen to contain "and" as a substring), so it wouldn't surface unless tested with different data.

**Verdict:** Single-client happy-path flows (login, one cashier doing transactions, one manager adding/updating books) would likely work, but the assignment's central requirement — concurrent multi-client access with thread synchronization — is not implemented at all, and the statistics-reporting feature (35/100 points) is functionally broken for the common single-winner case. Needs a Python 3 sandbox with two simultaneous client instances to concretely demonstrate the blocking/concurrency failure and the reports display bug.
