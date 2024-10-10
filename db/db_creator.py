import sqlite3

db = sqlite3.connect('mark.db')

db.execute('''CREATE TABLE TOOLS
(toolscode INT PRIMARY KEY NOT NULL,
name TEXT NOT NULL,
price REAL NOT NULL,
quantity INT NOT NULL);''')

db.execute('''CREATE TABLE EQUIPMENT
(equicode INT PRIMARY KEY NOT NULL,
name TEXT NOT NULL,
price REAL NOT NULL,
quantity INT NOT NULL);''')

db.execute("INSERT INTO TOOLS (toolscode, name, price, quantity) VALUES (1, 'Hammer', 500.00, 11)");
db.execute("INSERT INTO TOOLS (toolscode, name, price, quantity) VALUES (2, 'Drill', 600.00, 5)");
db.execute("INSERT INTO TOOLS (toolscode, name, price, quantity) VALUES (3, 'Saw', 700.00, 9)");
db.execute("INSERT INTO TOOLS (toolscode, name, price, quantity) VALUES (4, 'Screwdriver', 400.00, 12)");
db.execute("INSERT INTO TOOLS (toolscode, name, price, quantity) VALUES (5, 'Cutter', 200.00, 8)");
db.execute("INSERT INTO TOOLS (toolscode, name, price, quantity) VALUES (6, 'Wrench', 300.00, 21)");

db.execute("INSERT INTO EQUIPMENT (equicode, name, price, quantity) VALUES (1, 'Nails', 5.00, 100)");
db.execute("INSERT INTO EQUIPMENT (equicode, name, price, quantity) VALUES (2, 'Bolts', 4.00, 70)");
db.execute("INSERT INTO EQUIPMENT (equicode, name, price, quantity) VALUES (3, 'Screws', 8.00, 27)");
db.execute("INSERT INTO EQUIPMENT (equicode, name, price, quantity) VALUES (4, 'Tape', 20.00, 15)");
db.execute("INSERT INTO EQUIPMENT (equicode, name, price, quantity) VALUES (5, 'Pencils', 3.00, 86)");
db.execute("INSERT INTO EQUIPMENT (equicode, name, price, quantity) VALUES (6, 'Plugs', 2.00, 36)");

db.commit()
db.close()
