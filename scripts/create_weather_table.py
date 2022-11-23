import sqlite3

connection = sqlite3.connect("./clima.db")
cursor = connection.cursor()
cursor.execute("DROP TABLE IF EXISTS cities")

table = """CREATE TABLE cities(
            city text primary key,
			temperatura int
		);"""

cursor.execute(table)
cursor.execute("INSERT INTO cities values ('Madrid', 30)")
cursor.execute("INSERT INTO cities values ('Sidney', 32)")
cursor.execute("INSERT INTO cities values ('Londres', 9)")
cursor.execute("INSERT INTO cities values ('Alicante', 26)")
cursor.execute("INSERT INTO cities values ('Amsterdam', -5)")
cursor.execute("INSERT INTO cities values ('Wisconsin', -15)")
cursor.execute("INSERT INTO cities values ('San Sebastian', 4)")
cursor.execute("INSERT INTO cities values ('Texas', 15)")
cursor.execute("INSERT INTO cities values ('Nueva York', 20)")
cursor.execute("INSERT INTO cities values ('Montevideo', 22)")
cursor.execute("INSERT INTO cities values ('Buenos Aires', 22)")

print("TABLE CREATED: {}".format(table))
connection.commit()
connection.close()
