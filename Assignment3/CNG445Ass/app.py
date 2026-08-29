from flask import *
import sqlite3
import re

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

PASSWORD_RULE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{10,}$")

@app.route("/style.css")
def style():
    return send_from_directory(app.root_path, "style.css")

@app.route("/validation.js")
def validation():
    return send_from_directory(app.root_path, "validation.js")


@app.route("/")
@app.route("/index")
def index():
    msg = request.args.get("msg")
    
    # Capture Search Parameters
    keyword = request.args.get("keyword")
    soc_filter = request.args.get("society")

    conn = sqlite3.connect("portal.db")
    c = conn.cursor()

    #Get All Societies 
    c.execute("SELECT societyID, name FROM Society ORDER BY name")
    societies = c.fetchall()

    # Handle Search Logic
    search_results = None
    search_mode = None

    if keyword is not None:
        search_term = f"%{keyword}%"
        
        # Search All Societies
        if soc_filter == "all":
            search_mode = "all"
            search_results = {}
            
            
            for s in societies:
                search_results[s[1]] = [] 

            
            c.execute("""
                SELECT e.eventID, e.name, e.description, s.name
                FROM Event e
                JOIN involves i ON e.eventID = i.eventID
                JOIN Society s ON i.societyID = s.societyID
                WHERE (e.name LIKE ? OR e.description LIKE ?)
            """, (search_term, search_term))
            
            rows = c.fetchall()
            for row in rows:
                soc_name = row[3]
                if soc_name in search_results:
                    search_results[soc_name].append(row)

        # Search Specific Society
        else:
            search_mode = "specific"
            c.execute("""
                SELECT e.eventID, e.name, e.description, s.name
                FROM Event e
                JOIN involves i ON e.eventID = i.eventID
                JOIN Society s ON i.societyID = s.societyID
                WHERE i.societyID = ? AND (e.name LIKE ? OR e.description LIKE ?)
            """, (soc_filter, search_term, search_term))
            search_results = c.fetchall()

    # Get User's Own Events 
    my_events = []
    if session.get("username") and session.get("isAdmin") == 0:
        c.execute("""
            SELECT e.eventID, e.name, e.timeDate, e.description, e.entryPrice,
                   IFNULL(GROUP_CONCAT(s.name, ', '), '') AS soc_names
            FROM Event e
            LEFT JOIN involves i ON e.eventID = i.eventID
            LEFT JOIN Society s ON i.societyID = s.societyID
            WHERE e.username = ?
            GROUP BY e.eventID
            ORDER BY e.eventID DESC
        """, (session["username"],))
        my_events = c.fetchall()

    conn.close()

    return render_template("index.html",
                           username=session.get("username"),
                           isAdmin=session.get("isAdmin"),
                           error=None,
                           msg=msg,
                           societies=societies,
                           events=my_events,      # User's managed events
                           results=search_results, # Search results
                           keyword=keyword,
                           search_mode=search_mode,
                           selected_soc=soc_filter)
@app.route("/event_details/<int:event_id>")
def event_details(event_id):
    conn = sqlite3.connect("portal.db")
    c = conn.cursor()
    
    # Fetch Event info + Comma separated societies
    c.execute("""
        SELECT e.name, e.timeDate, e.description, e.entryPrice, 
               IFNULL(GROUP_CONCAT(s.name, ', '), '')
        FROM Event e
        LEFT JOIN involves i ON e.eventID = i.eventID
        LEFT JOIN Society s ON i.societyID = s.societyID
        WHERE e.eventID = ?
        GROUP BY e.eventID
    """, (event_id,))
    
    event = c.fetchone()
    conn.close()
    
    if event:
        return render_template("details.html", event=event)
    else:
        return redirect(url_for("index", msg="Event not found."))

#login routinf
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"].strip()
    password = request.form["password"]

    conn = sqlite3.connect("portal.db")
    c = conn.cursor()
    c.execute("SELECT username, isAdmin FROM User WHERE username=? AND password=?",
              (username, password))
    row = c.fetchone()
    conn.close()

    if row is not None:
        session["username"] = row[0]
        session["isAdmin"] = row[1]
        return redirect(url_for("index"))

    return redirect(url_for("index", msg="Invalid username or password."))


@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("isAdmin", None)
    return redirect(url_for("index"))

#register routing
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        name = request.form["name"].strip()
        email = request.form["email"].strip()

        if username == "" or password == "" or name == "" or email == "":
            return render_template("register.html", error="All fields are required.")
        # password compatability check
        if PASSWORD_RULE.match(password) is None:
            return render_template("register.html",
                                   error="Password must be include minimum 10 chars and lso include upper letters, lower letters and a digit.")

        isAdmin = 1 if email.startswith("org-") else 0

        conn = sqlite3.connect("portal.db")
        c = conn.cursor()

        c.execute("SELECT username FROM User WHERE username=?", (username,))
        if c.fetchone() is not None:
            conn.close()
            return render_template("register.html", error="Username already exists.")

        c.execute("INSERT INTO User(username,password,name,email,isAdmin) VALUES(?,?,?,?,?)",
                  (username, password, name, email, isAdmin))
        conn.commit()
        conn.close()

        return render_template("register_ok.html")

    return render_template("register.html", error=None)

#societies looking routing
@app.route("/societies", methods=["GET", "POST"])
def societies():
    if "username" not in session or session.get("isAdmin") != 1:
        return redirect(url_for("index"))

    if request.method == "POST":
        societyName = " ".join(request.form["societyName"].strip().split())
        if societyName == "":
            return show_societies_page("Society name cannot be empty.")

        conn = sqlite3.connect("portal.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO Society(name) VALUES(?)", (societyName,))
            conn.commit()
            conn.close()
            return redirect(url_for("societies"))
        except sqlite3.IntegrityError:
            conn.close()
            return show_societies_page("Society already exists.")

    return show_societies_page(None)


def show_societies_page(msg):
    conn = sqlite3.connect("portal.db")
    c = conn.cursor()

    c.execute("""
        SELECT s.societyID, s.name,
               COUNT(DISTINCT i.eventID) AS eventCount
        FROM Society s
        LEFT JOIN involves i ON i.societyID = s.societyID
        GROUP BY s.societyID
        ORDER BY s.name
    """)
    socs = c.fetchall()
    conn.close()

    return render_template("societies.html",
                           username=session.get("username"),
                           isAdmin=session.get("isAdmin"),
                           societies=socs,
                           error=msg)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "username" not in session:
        return redirect(url_for("index"))
    # reques/form processing start
    if request.method == "POST":
        newPassword = request.form["password"]
        newName = request.form["name"].strip()
        newEmail = request.form["email"].strip()

        if newName == "" or newEmail == "":
            return show_profile_page("Name and Email cannot be empty.")

        conn = sqlite3.connect("portal.db")
        c = conn.cursor()

        if newPassword != "":
            if PASSWORD_RULE.match(newPassword) is None:
                conn.close()
                return show_profile_page("Password must be include minimum 10 chars and lso include upper letters, lower letters and a digit.")
            c.execute("UPDATE User SET password=?, name=?, email=? WHERE username=?",
                      (newPassword, newName, newEmail, session["username"]))
        else:
            c.execute("UPDATE User SET name=?, email=? WHERE username=?",
                      (newName, newEmail, session["username"]))

        conn.commit()
        conn.close()
        return show_profile_page("Profile updated successfully.")

    return show_profile_page(None)


def show_profile_page(msg):
    conn = sqlite3.connect("portal.db")
    c = conn.cursor()
    c.execute("SELECT username, name, email, isAdmin FROM User WHERE username=?",
              (session["username"],))
    row = c.fetchone()
    conn.close()

    return render_template("profile.html",
                           username=session.get("username"),
                           isAdmin=session.get("isAdmin"),
                           profile=row,
                           message=msg)


# ONE events handler: insert/delete, then go back home
@app.route("/events", methods=["POST"])
def manage_events():
    if "username" not in session or session.get("isAdmin") == 1:
        return redirect(url_for("index", msg="Only normal users can add/delete events."))

    action_type = request.form.get("action_type")
    if action_type not in ("add_event", "delete_event"):
        return redirect(url_for("index", msg="Invalid action."))

    conn = sqlite3.connect("portal.db")
    c = conn.cursor()

    if action_type == "add_event":
        event_name = request.form.get("event_name", "").strip()
        timeDate = request.form.get("event_timeDate", "").strip()
        description = request.form.get("description", "").strip()
        fee_type = request.form.get("fee_type")          # must be 'free' or 'paid'
        soc_ids = request.form.getlist("societies")

        if event_name == "" or timeDate == "" or description == "":
            conn.close()
            return redirect(url_for("index", msg="Event not added: missing fields."))

        if fee_type not in ("free", "paid"):
            conn.close()
            return redirect(url_for("index", msg="Event not added: choose Free or Paid."))

        if len(soc_ids) == 0:
            conn.close()
            return redirect(url_for("index", msg="Event not added: select at least one society."))

        if fee_type == "free":
            entryPrice = 0.0
        else:
            fee_txt = request.form.get("entryPrice", "").strip()
            try:
                entryPrice = float(fee_txt)
            except ValueError:
                conn.close()
                return redirect(url_for("index", msg="Event not added: fee must be numeric."))

        # unique event name
        c.execute("SELECT name FROM Event WHERE name=?", (event_name,))
        if c.fetchone() is not None:
            conn.close()
            return redirect(url_for("index", msg="Event not added: event name already exists."))

        c.execute(
            "INSERT INTO Event(name, timeDate, description, entryPrice, username) VALUES (?,?,?,?,?)",
            (event_name, timeDate, description, entryPrice, session["username"])
        )
        event_id = c.lastrowid

        for sid in soc_ids:
            c.execute("INSERT INTO involves(eventID, societyID) VALUES (?,?)", (event_id, int(sid)))

        conn.commit()
        conn.close()
        return redirect(url_for("index", msg="Event added successfully."))

    # delete_event
    event_id = int(request.form.get("event_id", "0"))
    c.execute("SELECT username FROM Event WHERE eventID=?", (event_id,))
    row = c.fetchone()

    if row is None or row[0] != session["username"]:
        conn.close()
        return redirect(url_for("index", msg="Cannot delete: not your event."))

    c.execute("DELETE FROM involves WHERE eventID=?", (event_id,))
    c.execute("DELETE FROM Event WHERE eventID=?", (event_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index", msg="Event deleted."))


if __name__ == "__main__":
    app.run(debug=True)
