# db.py
import sqlite3
import pandas as pd

DB_NAME = "expenses.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_str TEXT,
            label TEXT,
            amount REAL,
            comment TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def insert_expense(date_str, label, amount, comment):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO expenses (date_str, label, amount, comment) VALUES (?, ?, ?, ?)",
                (date_str, label, amount, comment))
    conn.commit()
    conn.close()

def delete_last_expense():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id = (SELECT MAX(id) FROM expenses)")
    conn.commit()
    conn.close()

def get_all_expenses():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM expenses ORDER BY timestamp DESC", conn)
    conn.close()
    return df

