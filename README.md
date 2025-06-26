# 🏦 Retail Banking Web Application (Flask + SQLite)

A simple, secure retail banking system built using **Flask** and **SQLite**, allowing users to:

- Register & log in
- Create bank accounts
- Deposit & withdraw money
- Transfer funds between accounts
- View account balances
- View detailed transaction history

---

## 🚀 Features

- ✅ User authentication (login/logout/register)
- ✅ Login-required protected routes
- ✅ Create new bank accounts
- ✅ Deposit & withdraw money
- ✅ Transfer money between accounts
- ✅ Track all transactions with type, amount, time
- ✅ Clean Bootstrap UI
- ✅ Dockerized for easy deployment

---

## 🛠 Tech Stack

- **Python** (Flask)
- **SQLite3** (Database)
- **HTML/CSS + Bootstrap** (UI)
- **Docker** (Deployment)

---

## 🗂 Folder Structure
```
retail_bank_app/
├── app.py
├── Dockerfile
├── requirements.txt
├── banking.db (auto-created)
├── templates/
│ ├── index.html
│ ├── login.html
│ ├── register.html
│ ├── create_account.html
│ ├── deposit.html
│ ├── withdraw.html
│ ├── transfer.html
│ ├── check_balance.html
│ └── transactions.html
```

---

## ⚙️ Setup Instructions (Without Docker)

1. **Clone the repository**
```bash
git clone https://github.com/Raket-Swathi/secure_bank_app.git
```
---
```
##📋 User Flow 
User registers or logs in

Creates a bank account (name + initial balance)

Can now:

-Deposit to any account

-Withdraw from any account

-Transfer funds between accounts

-View current balances

-View full transaction history
```
---

```
📂 Database Schema
1)users

id (int)

username (text)

password (text)

2)accounts

id (int)

name (text)

balance (real)

3)transactions

id (int)

acc_id (int)

name (text)

type (text)

amount (real)

time (timestamp)
```
---
```
✅ Sample Credentials (for testing)
You can register any user from the UI and log in to test features.
```
