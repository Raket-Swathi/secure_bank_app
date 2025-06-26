from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# 🔐 Login-required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 🛠 Initialize database
def init_db():
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Accounts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            balance REAL NOT NULL
        )
    ''')

    # Transactions log table
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            acc_id INTEGER,
            name TEXT,
            type TEXT,
            amount REAL,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# 🏠 Home
@app.route('/')
def home():
    return render_template("index.html")

# 👤 Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('bank.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            msg = "Registration successful. Please login."
        except sqlite3.IntegrityError:
            msg = "Username already exists."
        conn.close()
    return render_template("register.html", message=msg)

# 🔐 Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('bank.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            msg = "Invalid username or password."
    return render_template("login.html", message=msg)

# 🚪 Logout
@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# 🏦 Create account
@app.route('/create_account', methods=['GET', 'POST'])
@login_required
def create_account():
    msg = ''
    if request.method == 'POST':
        name = request.form['name']
        balance = float(request.form['balance'])
        conn = sqlite3.connect('bank.db')
        c = conn.cursor()
        c.execute("INSERT INTO accounts (name, balance) VALUES (?, ?)", (name, balance))
        conn.commit()
        conn.close()
        msg = "Account created successfully."
    return render_template("create_account.html", message=msg)

# 💰 Deposit
@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    msg = ''
    if request.method == 'POST':
        acc_id = request.form['acc_id']
        amount = float(request.form['amount'])
        conn = sqlite3.connect('bank.db')
        c = conn.cursor()

        c.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, acc_id))
        if c.rowcount == 0:
            msg = "Account not found."
        else:
            c.execute("SELECT name FROM accounts WHERE id = ?", (acc_id,))
            name = c.fetchone()
            if name:
                c.execute("INSERT INTO transactions (acc_id, name, type, amount) VALUES (?, ?, 'deposit', ?)",
                          (acc_id, name[0], amount))
            conn.commit()
            msg = f"Deposited ₹{amount:.2f} to Account {acc_id}."
        conn.close()
    return render_template("deposit.html", message=msg)

# 💸 Withdraw
@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    msg = ''
    if request.method == 'POST':
        acc_id = request.form['acc_id']
        amount = float(request.form['amount'])
        conn = sqlite3.connect('bank.db')
        c = conn.cursor()

        c.execute("SELECT balance FROM accounts WHERE id = ?", (acc_id,))
        acc = c.fetchone()
        if not acc:
            msg = "Account not found."
        elif acc[0] < amount:
            msg = "Insufficient balance."
        else:
            c.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, acc_id))
            c.execute("SELECT name FROM accounts WHERE id = ?", (acc_id,))
            name = c.fetchone()
            if name:
                c.execute("INSERT INTO transactions (acc_id, name, type, amount) VALUES (?, ?, 'withdraw', ?)",
                          (acc_id, name[0], amount))
            conn.commit()
            msg = f"Withdrawn ₹{amount:.2f} from Account {acc_id}."
        conn.close()
    return render_template("withdraw.html", message=msg)

# 🔁 Transfer
@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    msg = ''
    if request.method == 'POST':
        from_id = request.form['from_id']
        to_id = request.form['to_id']
        amount = float(request.form['amount'])
        conn = sqlite3.connect('bank.db')
        c = conn.cursor()

        c.execute("SELECT balance, name FROM accounts WHERE id=?", (from_id,))
        from_acc = c.fetchone()

        c.execute("SELECT name FROM accounts WHERE id=?", (to_id,))
        to_acc = c.fetchone()

        if not from_acc:
            msg = "Sender account not found."
        elif from_acc[0] < amount:
            msg = "Insufficient balance."
        elif not to_acc:
            msg = "Recipient account not found."
        else:
            c.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, from_id))
            c.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, to_id))
            c.execute("INSERT INTO transactions (acc_id, name, type, amount) VALUES (?, ?, 'transfer-out', ?)",
                      (from_id, from_acc[1], amount))
            c.execute("INSERT INTO transactions (acc_id, name, type, amount) VALUES (?, ?, 'transfer-in', ?)",
                      (to_id, to_acc[0], amount))
            conn.commit()
            msg = f"Transferred ₹{amount:.2f} from Account {from_id} to Account {to_id}."
        conn.close()
    return render_template("transfer.html", message=msg)

# 📄 Check current balances
@app.route('/check_balance')
@login_required
def check_balance():
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    c.execute("SELECT id, name, balance FROM accounts")
    balances = c.fetchall()
    conn.close()
    return render_template("check_balance.html", balances=balances)

# 📜 View transaction history
@app.route('/transactions')
@login_required
def transactions():
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    c.execute("SELECT acc_id, name, type, amount, time FROM transactions ORDER BY time DESC")
    txns = c.fetchall()
    conn.close()
    return render_template("transactions.html", txns=txns)

# 🚀 Run Flask app
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0',debug=True, port=5050)

