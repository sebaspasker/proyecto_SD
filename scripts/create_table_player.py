import sqlite3

connection = sqlite3.connect("../againstall.db")
cursor = connection.cursor()
cursor.execute("DROP TABLE IF EXISTS players")

table = """ CREATE TABLE players(
            alias text primary key,
			pass text not null,
			x integer,
			y integer,
			level integer,
			ec integer,
			ef integer,
			dead integer
		);"""

cursor.execute(table)
cursor.execute("INSERT INTO players values ('Jesus', '123', 1, 1, 0, 0, 0, 0)")
cursor.execute("INSERT INTO players values ('Sebas', '123', 2, 1, 0, 0, 0, 0)")

print("TABLE CREATED: {}".format(table))
connection.commit()
connection.close()
