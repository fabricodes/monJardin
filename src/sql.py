import sqlite3 as sql

conn=sql.connect('plantes')
cur = conn.cursor()

req="SELECT DISTINCT hauteur FROM especes;"
cursor = cur.execute(req)
rows= cursor.fetchall()
conn.close()

for row in rows:
    for item in row:
        print (item, end=" " )
        print()
