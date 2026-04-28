# Created on: 2026-04-28

import mysql.connector

connector = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Hkoradiya',
    database='ss'
)
cursor = connector.cursor()


query = "INSERT INTO emp (name, dept_id) VALUES (%s, %s), (%s, %s), (%s, %s)"
values = ('gautam', 1, 'pari', 1, 'paro', 2)
cursor.execute(query, values)

cursor.execute("select * from emp")
rows = cursor.fetchall()

for row in rows:
    print(row)
    
cursor.close()
connector.close()

