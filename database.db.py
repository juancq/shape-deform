import sqlite3
import os.path

def dataEntry(equation):
    '''
        Function for entering equations into the database. Pass in the equation as a string to the function.
        eg: dataEntry('sin(45) * time - y')
    '''
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM equations")

    ID = []

    for col in c.fetchall():
        ID.append(col[0])

    c.execute("INSERT INTO equations (ID, equation) VALUES (?, ?)", (len(ID)+1, equation))

    conn.commit()

    c.close()
    conn.close()

# dataEntry('Enter Equation Here')

if(not os.path.exists('database.db')):
    conn = sqlite3.connect('database.db')
    print "Database created successfully"

    conn.execute("CREATE TABLE IF NOT EXISTS equations(id INTEGER PRIMARY KEY AUTOINCREMENT, equation TEXT)")

    conn.execute("CREATE TABLE IF NOT EXISTS models(id INTEGER PRIMARY KEY AUTOINCREMENT, modelName TEXT)")
    print "Tables created successfully"
    conn.close()
else:
    print "Both database and the tables already exists"
