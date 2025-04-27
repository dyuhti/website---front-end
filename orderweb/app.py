from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database setup
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Hash function for password security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route("/signup", methods=["POST"])
def signup():
    name = request.form["name"]
    email = request.form["email"]
    password = hash_password(request.form["password"])

    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        conn.close()
        return redirect(url_for("login_page"))  # ✅ Corrected redirect to login page
    except sqlite3.IntegrityError:
        return "Email already exists. Try logging in."


# Login route
@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = hash_password(request.form["password"])

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session["user"] = user[1]  # Store the name in session
        return redirect(url_for("dashboard"))
    else:
        return "Invalid login credentials. Try again."

# Dashboard route (after login)
@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return f"Welcome {session['user']}! <a href='/logout'>Logout</a>"
    else:
        return redirect(url_for("login_page"))

# Logout route
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login_page"))

# Serve login page
@app.route("/")
@app.route("/login")
def login_page():
    return render_template("login.html")

# Serve sign-up page
@app.route("/signup_page")
def signup_page():
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)
