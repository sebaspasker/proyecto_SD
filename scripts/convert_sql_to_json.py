import json
import sqlite3
from hashlib import md5


DB_SERVER = "./againstall.db"
JSON_MAP = "./json/map.json"
JSON_USER = "./json/users.json"
connection = sqlite3.connect(DB_SERVER)
cursor = connection.cursor()

users_ = cursor.execute("select * from players;").fetchall()
map_ = cursor.execute("select * from map_engine;").fetchall()

connection.close()

user_dict = {}
map_dict = {}

for user in users_:
    user_dict[user[0]] = {
        "alias": user[0],
        "pass": md5(user[1].encode("utf-8")).hexdigest(),
        "level": user[2],
        "ec": user[3],
        "ef": user[4],
        "dead": user[5],
        "active": user[6],
    }

for map__ in map_:
    map_dict = {
        "map": map__[1],
        "weather": {
            "None1": 15,
            "None2": 15,
            "None3": 15,
            "None4": 15,
        },
    }

with open(JSON_MAP, "w") as f:
    json.dump(map_dict, f)

with open(JSON_USER, "w") as f:
    json.dump(user_dict, f)
