import sqlite3
import client
conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute("INSERT INTO site1 VALUES (?)", ('' , '', client.GeneratePassword(), '' )) # Добавление данных
conn.commit()