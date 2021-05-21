import sqlite3


connection = sqlite3.connect("test.db")
cursor = connection.cursor()

cursor.executescript(open("test_db.sql", "r").read())