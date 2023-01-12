import json

# COPIAR CUANDO CAMBIEMOS PARÁMETROS
data = {
    "IP_ENGINE": "172.20.40.175",
    "PORT_ENGINE": 5050,
    "IP_REG": "172.20.40.175",
    "PORT_REG": 5051,
    "IP_WEATHER": "127.0.0.3",
    "PORT_WEATHER": 5052,
    "KAFKA_SERVER": "192.20.40.174:9092",
    "FORMAT": "utf-8",
    "DB_SERVER": "againstall.db",
    "MAX_USERS": 4,
    "TIME_WAIT_SEC": 30,
    "HEADER": 64,
    "NUMBER_NPC": 4,
    "RESET": "NO",
    "CITIES_JSON": "./json/cities.json",
    "PRIVATE_KEY_USER": "./pem/private_key_player.pem",
}

# COPIAR CUANDO CAMBIEMOS PARÁMETROS
data_lab = {
    "IP_ENGINE": "172.20.40.175",
    "PORT_ENGINE": 5050,
    "IP_REG": "172.20.40.175",
    "PORT_REG": 5051,
    "IP_WEATHER": "172.20.40.174",
    "PORT_WEATHER": 5052,
    "KAFKA_SERVER": "172.20.40.174:9092",
    "FORMAT": "utf-8",
    "DB_SERVER": "againstall.db",
    "MAX_USERS": 4,
    "TIME_WAIT_SEC": 60,
    "HEADER": 64,
    "NUMBER_NPC": 3,
    "RESET": "NO",
}

with open("./config/config_lab_2.json", "w") as outfile:
    str_ = json.dumps(data)
    outfile.write(str_)
