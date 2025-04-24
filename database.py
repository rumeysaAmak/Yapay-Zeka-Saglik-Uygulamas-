import sqlite3

def create_db():
    conn = sqlite3.connect('contact_form.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS contacts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  phone TEXT NOT NULL,
                  email TEXT NOT NULL,
                  subject TEXT NOT NULL,
                  message TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def insert_contact(name, phone, email, subject, message):
    conn = sqlite3.connect('contact_form.db')
    c = conn.cursor()
    c.execute("INSERT INTO contacts (name, phone, email, subject, message) VALUES (?, ?, ?, ?, ?)",
              (name, phone, email, subject, message))
    conn.commit()
    conn.close()
# Uygulama başlatıldığında veritabanı otomatik olarak oluşturulsun
create_db()
