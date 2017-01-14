import sqlite3

conn = sqlite3.connect('database.db')
print "Opened database successfully";

conn.execute('create table equations (id integer primary key autoincrement,'
             ' equation TEXT)')

print "Table created successfully";
conn.close()