import sqlite3

connection = sqlite3.connect("./againstall.db")
cursor = connection.cursor()
cursor.execute("DROP TABLE IF EXISTS players")
cursor.execute("DROP TABLE IF EXISTS player_id")
cursor.execute("DROP TABLE IF EXISTS map_engine")

# table_p = """ CREATE TABLE players(
#             alias text primary key,
# 			pass text not null,
# 			x integer,
# 			y integer,
# 			level integer,
# 			ec integer,
# 			ef integer,
# 			dead integer,
#             active boolean not null
# 		);"""

table_p = """ CREATE TABLE players(
            alias text primary key,
			pass text not null,
			level integer,
			ec integer,
			ef integer,
			dead integer,
            active boolean not null
		);"""


table_alias = """
            CREATE TABLE player_id(
                id integer primary key autoincrement not null,
                alias text unique,
                active boolean not null,
                foreign key (alias) references players(alias)
            );"""

table_map = """
CREATE TABLE map_engine(
    id integer primary key,
    map varchar(400) not null
    );"""

cursor.execute(table_p)
cursor.execute(table_alias)
cursor.execute(table_map)
cursor.execute("INSERT INTO players values ('Jesus', '123', 0, 0, 0, 0, 0)")
cursor.execute("INSERT INTO players values ('Sebas', '123', 0, 0, 0, 0, 0)")
cursor.execute("INSERT INTO player_id(alias, active) values('Jesus', 1)")
cursor.execute("INSERT INTO player_id(alias, active) values('Sebas', 1)")
cursor.execute("INSERT INTO map_engine(id, map) values(0, '')")

print("TABLE CREATED: {}".format(table_p))
print("TABLE CREATED: {}".format(table_alias))
print("TABLE CREATED: {}".format(table_map))
connection.commit()
connection.close()
