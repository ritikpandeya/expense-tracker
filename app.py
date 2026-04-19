from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
import pandas as pd

app = Flask(__name__)
app.secret_key = "secret123"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        amount REAL,
        category TEXT,
        date TEXT
    )""")
    conn.commit()
    conn.close()

init_db()

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            user = User(1)
            login_user(user)
            return redirect("/")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route("/")
@login_required
def home():
    return render_template("index.html")

@app.route("/add", methods=["POST"])
@login_required
def add():
    data = request.json
    date = datetime.now().strftime("%d %b %Y %I:%M %p")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO transactions(text,amount,category,date) VALUES(?,?,?,?)",
                (data["text"], data["amount"], data["category"], date))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route("/get")
@login_required
def get():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions ORDER BY id DESC")
    data = cur.fetchall()
    conn.close()
    return jsonify(data)

@app.route("/delete/<int:id>", methods=["DELETE"])
@login_required
def delete(id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM transactions WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route("/clear", methods=["DELETE"])
@login_required
def clear():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route("/export")
@login_required
def export():
    conn = sqlite3.connect("database.db")
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    df.to_csv("transactions.csv", index=False)
    return jsonify(success=True)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)