import ast
import json
import socket
import sqlite3
import sys
import threading
import random
import requests
from time import sleep, time
from pprint import pprint
from src.Map import Map
from src.Player import Player
from src.NPC import NPC
from src.utils.Sockets_dict import dict_sockets
from src.utils.Sockets_dict import dict_send_error
from src.utils.Process_position import process_position
from src.utils.assymetric_encryption import *
from kafka import KafkaProducer, KafkaConsumer


if len(sys.argv) == 2:
    with open(sys.argv[1]) as f:
        JSON_CFG = json.load(f)

    IP_SOCKET = JSON_CFG["IP_ENGINE"]
    PUERTO_SOCKET = JSON_CFG["PORT_ENGINE"]
    IP_WEATHER = JSON_CFG["IP_WEATHER"]
    PUERTO_WEATHER = JSON_CFG["PORT_WEATHER"]
    KAFKA_SERVER = JSON_CFG["KAFKA_SERVER"]
    DB_SERVER = JSON_CFG["DB_SERVER"]
    FORMAT = JSON_CFG["FORMAT"]
    MAX_USERS = JSON_CFG["MAX_USERS"]
    TIME_WAIT_SEC = JSON_CFG["TIME_WAIT_SEC"]
    HEADER = JSON_CFG["HEADER"]
    RESET = JSON_CFG["RESET"]
    CITIES_JSON = JSON_CFG["CITIES_JSON"]
    # TODO Cambiar a parámetro de json
    JSON_MAP = "./json/map.json"
    JSON_USERS = "./json/users.json"

MAP = Map()
WEATHER_DICT = {}

CHANGE = False
WAIT_USER = True

PRIVATE_KEY = None

sys.path.append("src")
sys.path.append("src/exceptions")

players_dict = {}
npc_dict = {}
rsa_dict = {}

####### NEW UPDATE P3 #######
def save_map_and_weather_json():
    while True:
        sleep(1)
        with open(JSON_MAP, "w") as f:
            json.dump({"map": MAP.to_raw_string(), "weather": WEATHER_DICT}, f)


def save_dict_players_json():
    while True:
        sleep(1)
        with open(JSON_USERS, "w") as f:
            dict_json = {}
            for key in players_dict:
                dict_json[key] = players_dict[key].get_dict()
            json.dump(dict_json, f)


def exchange_keys(alias, connection):
    global rsa_dict

    public_key_byte = bytearray(get_public_key_bytes(PRIVATE_KEY.public_key()))
    connection.send(public_key_byte)

    public_key_cli = read_public_key_bytes(connection.recv(512))
    rsa_dict[alias] = public_key_cli


#############################


def reset_map():
    global MAP
    read_players()
    MAP = read_map()


def save_state_map():
    while True:
        sleep(5)
        save_map(MAP)
        save_players(players_dict)


def see_winner():
    print("[SEARCHING WINNER] Started searching a winner.")
    while True:
        sleep(5)
        alias_alive = []
        for key in players_dict.keys():
            if players_dict[key].get_dead() is False:
                alias_alive.append(key)
        if len(alias_alive) == 1:
            producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
            while True:
                producer.send(
                    "winner_{}".format(alias_alive[0][0].lower()), "1".encode(FORMAT)
                )


def connect_db(name=None):
    """
    Connect a ddbb and returns a cursor.
    """
    if name is None:
        connection = sqlite3.connect(DB_SERVER)
        return sqlite3.connect(DB_SERVER).cursor(), connection
    else:
        connection = sqlite3.connect(name)
        return sqlite3.connect(name).cursor(), connection


def reset_values():
    """
    Reset values of the ddbb.
    """

    cursor, connection = connect_db()
    cursor.execute("update players set dead = 0, level = 0, ec = 0, ef = 0;")
    connection.commit()
    connection.close()


def create_map():
    """
    Create a map game and saves it in the ddbb.
    """

    print("[CREATING MAP] Creating the map and saving in the ddbb.")

    global map_engine
    map_engine = Map()

    connection = sqlite3.connect(DB_SERVER)
    cursor = connection.cursor()

    connection.commit()
    save_map(map_engine)
    global MAP
    MAP = read_map()
    MAP.set_none_influencial_weather()

    connection.commit()
    connection.close()


def save_player_position(connection, cursor, alias, x, y):
    cursor.execute(
        "update players set x = {}, y = {} where alias = '{}'".format(x, y, alias)
    )


@DeprecationWarning
def actualize_players_position():
    connection = sqlite3.connect(DB_SERVER)
    cursor = connection.cursor()
    id_rows = cursor.execute("select * from players where active = 1").fetchall()
    map_ = read_map()
    for row in id_rows:
        x, y = random.randint(1, 18), random.randint(1, 18)
        if row[0] in players_dict.keys():
            map_.set_map_matrix(x, y, row[0].lower()[0])
            save_player_position(connection, cursor, row[0], x, y)
            players_dict[row[0]].set_position(int(x), int(y))

    connection.commit()
    connection.close()
    save_map(map_)


def save_map(map_to_saved):
    connection = sqlite3.connect(DB_SERVER)
    cursor = connection.cursor()

    cursor.execute(
        "update map_engine set map='{}' where id={};".format(
            map_to_saved.to_raw_string(), 0
        )
    )

    connection.commit()
    connection.close()


def save_players(dict_players):
    connection = sqlite3.connect(DB_SERVER)
    cursor = connection.cursor()

    for key in list(dict_players.keys()):
        player = dict_players[key]
        cursor.execute(
            "update players set level={}, ec={}, ef={}, dead={}, active=1 where alias='{}';".format(
                player.get_level(),
                player.get_cold(),
                player.get_hot(),
                int(player.get_dead()),
                player.get_alias(),
            )
        )

    connection.commit()
    connection.close()


def read_players():
    global players_dict
    connection = sqlite3.connect(DB_SERVER)
    cursor = connection.cursor()

    cursor.execute("select * from players where active=1")

    players_msg = cursor.fetchall()
    for player_msg in players_msg:
        player = Player()
        player.set_alias(player_msg[0])
        player.set_level(player_msg[2])
        player.set_cold(player_msg[3])
        player.set_hot(player_msg[4])
        if player_msg[5] == 0:
            player.set_dead(False)
        else:
            player.set_dead(True)
        players_dict[player.get_alias()] = player

    connection.close()


@DeprecationWarning
def start_game_server(kafka_server=None):
    """
    Waits 60 second until the number of connected are max or
    time passes and starts the game
    """

    global SENDING_MAP
    global MAP_CREATED

    producer = (
        KafkaProducer(bootstrap_servers=KAFKA_SERVER)
        if kafka_server is None
        else KafkaProducer(bootstrap_servers=kafka_server)
    )

    print(
        "[WAITING FOR USERS] Waiting {} seconds until users are connected...".format(
            str(TIME_WAIT_SEC)
        )
    )

    WAIT_STARTED = True

    if MAP_CREATED is False:
        thread_create_map = threading.Thread(target=create_map, args=())
        thread_create_map.start()

    # Waits users
    for t in range(0, TIME_WAIT_SEC):
        producer.send(
            "start_game",
            bytes(dict_sockets()["Start_Waiting"].format(connected=CONNECTED), FORMAT),
        )
        if CONNECTED == MAX_USERS:
            break
        sleep(1)

    # Send user that the game starts
    if CONNECTED > 1:
        for t in range(0, 4):
            producer.send(
                "start_game",
                bytes(dict_sockets()["Start"].format(connected=CONNECTED), FORMAT),
            )
            sleep(0.5)

    if not SENDING_MAP:
        SENDING_MAP = True
        thread_send_map = threading.Thread(target=send_map, args=())
        thread_send_map.start()


def read_map(ddbb_server=None):
    """
    Reads the map in the ddbb and saves it in map_read variable.
    """

    try:
        cursor, connection = connect_db(DB_SERVER)

        cursor.execute("select * from map_engine where id =0")

        map_str = cursor.fetchone()[1]

        map_read = Map(map_str)
        # print(
        #     "[READING MAP] Reading map from database {} and saved in map_read.".format(
        #         DB_SERVER
        #     )
        # )

        return map_read
    except ValueError as VE:
        print("VALUE ERROR: Cerrando engine...")
        print("{}".format(VE.message))


def recieve_map(server):
    """
    Recieves a map with kafka and saves it in map_rec.
    """

    global map_rec

    try:
        consumer = KafkaConsumer("map_engine", bootstrap_servers=server)
        map_str = ""
        for message in consumer:
            map_str += message

        map_rec = Map(map_str)
        print(
            "[RECIEVING MAP] Recieved map raw char in topic '{}'".format("map_engine")
        )

    except ValueError as VE:
        print("VALUE ERROR: Cerrando engine...")
        print("{}".format(VE.message))


def read_client(alias, passwd) -> Player:
    """
    Read a client from the ddbb and returns the player.
    """
    cursor, connection = connect_db()
    if len(alias) <= 10 and len(passwd) <= 10:
        player_string = cursor.execute(
            "select * from players where alias = '{}' and pass = '{}'".format(
                alias, passwd
            )
        ).fetchone()

        if player_string:
            if player_string[0] == alias and player_string[1] == passwd:
                player = Player()
                player.set_alias(player_string[0])
                player.set_password(player_string[1])
                player.set_level(player_string[2])
                player.set_cold(player_string[3])
                player.set_hot(player_string[4])
                if player_string[5] == 0:
                    player.set_dead(False)
                else:
                    player.set_dead(True)
                return player
            else:
                print("[WARNING] Player not found.")
    else:
        print("[ERROR] Parameters of client too big.")
    return None


def wait_until_change():
    global CHANGE
    time_1 = time()
    while True:
        if CHANGE:
            return True
        if time_1 <= time() - 1:
            return True
        sleep(0.01)


def send_map(server=None):
    """
    Sends a map with kafka to 'map_engine' topic.
    """

    global CHANGE

    if server is None:
        producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
    else:
        producer = KafkaProducer(bootstrap_servers=server)

    print("[SENDING MAP] Sending map raw char to topic '{}'".format("map_engine"))

    while True:
        wait_until_change()
        try:
            producer.send("map_engine", MAP.to_raw_string().encode(FORMAT))
            CHANGE = False
        except ValueError as VE:
            print("VALUE ERROR: Cerrando engine...")
            print("{}".format(VE.message))


def send_server_active():
    """
    Send a signal to indicate server is alive.
    """
    producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

    print("[SENDING SERVER SIGNAL] Sending server signal.")

    while True:
        if WAIT_USER:
            producer.send("server", "1,{}".format(str(time())).encode(FORMAT))
        else:
            producer.send("server", "2,{}".format(str(time())).encode(FORMAT))
        sleep(1)


def send_weather(server=None):
    """
    Send the weather to kafka
    """
    producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

    print("[SENDING WEATHER] Sending weather to topic 'weather'")
    while True:
        try:
            weather = MAP.get_weather()
            keys = list(weather.keys())
            producer.send(
                "weather",
                dict_sockets()["Weather"]
                .format(
                    city_1=keys[0],
                    t_1=weather[keys[0]],
                    city_2=keys[1],
                    t_2=weather[keys[1]],
                    city_3=keys[2],
                    t_3=weather[keys[2]],
                    city_4=keys[3],
                    t_4=weather[keys[3]],
                )
                .encode(FORMAT),
            )
            sleep(1)
        except e:
            print(
                "[WEATHER SEND ERROR] Ha habido un error a la hora de enviar el weather..."
            )
            print(e)

            break


def see_new_position(position, key):
    if key == "w":
        return (position[0] - 1 if position[0] > 0 else 19, position[1])
    elif key == "a":
        return (position[0], position[1] - 1 if position[1] > 0 else 19)
    elif key == "s":
        return (position[0] + 1 if position[0] < 19 else 0, position[1])
    elif key == "d":
        return (position[0], position[1] + 1 if position[1] < 19 else 0)
    else:
        return None


@DeprecationWarning
def send_player(alias):
    global CHANGE

    kafka_producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

    player = players_dict[alias]
    while True:
        i = 0
        while not CHANGE:
            sleep(0.05)
            i += 1
            if i == 20:
                break
        CHANGE = False
        kafka_producer.send(
            "player_{}".format(alias[0].lower()),
            dict_sockets()["Player"]
            .format(
                alias=alias,
                level=str(player.get_level()),
                hot=str(player.get_hot()),
                cold=str(player.get_cold()),
                dead=str(player.get_dead()),
            )
            .encode(FORMAT),
        )


@DeprecationWarning
def process_player_dead(player):
    global dead_list
    dead_list.append(player.get_alias())


@DeprecationWarning
def process_key_old(key, position_, player):
    global CHANGE
    act_map = read_map()
    position = process_position(position_)
    new_position = see_new_position(position, key)
    if new_position is None:
        return False
    player = act_map.evaluate_move(position, new_position, player)
    # print(player)
    if player is not None:
        players_dict[player.get_alias()] = player
        if player.get_dead():
            process_player_dead(player)
    save_map(act_map)
    if player is not None:
        CHANGE = True
    return player


@DeprecationWarning
def process_client_msg(msg_):
    msg = msg_.split(",")  # Separate msg by comma
    if msg[0] != "6":
        return False
    # if int(msg[3]) <= last_id_msg[Alias]:
    #     return False
    key = msg[1]
    position = msg[2]  # Different format
    move_id = int(msg[3])
    alias = msg[4]
    if alias in dead_list:
        return None
    new_player = process_key(key, position, players_dict[alias])

    if new_player is not False and new_player is not None:
        producer_player = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
        producer_player.send(
            "player_{}".format(alias[0].lower()),
            bytes(
                dict_sockets()["Player"].format(
                    x=str(new_player.get_position()[0]),
                    y=str(new_player.get_position()[1]),
                    alias=new_player.get_alias(),
                    level=str(new_player.get_level()),
                    hot=str(new_player.get_hot()),
                    cold=str(new_player.get_cold()),
                    dead=str(new_player.get_dead()),
                ),
                FORMAT,
            ),
        )
        players_dict[alias] = new_player


@DeprecationWarning
def resolve_user_old(kafka_server=None):
    global MOVE_RECEIVER, RESOLVING_USER

    RESOLVING_USER = True

    producer = (
        KafkaProducer(bootstrap_servers=KAFKA_SERVER)
        if kafka_server is None
        else KafkaProducer(bootstrap_servers=kafka_server)
    )

    for t in range(0, 8):
        producer.send(
            "start_game",
            bytes(dict_sockets()["Start_Game"].format(connected=CONNECTED), FORMAT),
        )
        sleep(0.5)

    if MOVE_RECEIVER is False:
        MOVE_RECEIVER = True
        consumer = KafkaConsumer(
            # "move_player_{}".format(player.get_alias()[0]),
            "move_player",
            bootstrap_servers=KAFKA_SERVER,
        )

        for msg in consumer:
            thread_process_client_msg = threading.Thread(
                target=process_client_msg, args=[msg.value.decode(FORMAT)]
            )
            thread_process_client_msg.start()


def string_format_player(player):
    return dict_sockets()["Player"].format(
        alias=player.get_alias(),
        level=str(player.get_level()),
        hot=str(player.get_hot()),
        cold=str(player.get_cold()),
        dead=str(player.get_dead()),
    )


@DeprecationWarning
def string_socket_format_player(player):
    return dict_sockets()["Player"].format(
        x=str(player.get_position()[0]),
        y=str(player.get_position()[1]),
        alias=player.get_alias(),
        level=str(player.get_level()),
        hot=str(player.get_hot()),
        cold=str(player.get_cold()),
        dead=str(player.get_dead()),
    )


def login_client(connection, address):
    """
    Handle client login
    """
    while True:
        msg = connection.recv(HEADER).decode(FORMAT)
        if msg:
            params_login = msg.split(",")
            if params_login[0] == "3":
                player = read_client(params_login[1], params_login[2])
                if player is not None or (
                    player.get_alias() not in players_dict and RESET == "YES"
                ):
                    # TODO Mirar recien sacado
                    if RESET == "NO" or MAX_USERS <= len(players_dict.keys()):
                        player.reset_game()
                        players_dict[player.get_alias()] = player
                    connection.send(dict_sockets()["Correct"].encode(FORMAT))
                    connection.send(
                        string_format_player(players_dict[player.get_alias()]).encode(
                            FORMAT
                        )
                    )
                    print(
                        "[LOGIN] User with IP {} and alias {} have logged in.".format(
                            address[0], player.get_alias()
                        )
                    )

                    return player.get_alias()
                else:
                    print("[LOGIN ERROR] User with IP {} could not login.")
                    connection.send(dict_sockets()["Incorrect"].encode(FORMAT))


def random_npc_distribution():
    """
    Distribute active npcs in map.
    """

    # TODO Hacer que lo distribuya, actualice la posición en AA_NPC
    # y a partir de ahí se mueva
    global MAP
    for npc in npc_dict.values():
        MAP.npc_random_position(npc)


def random_player_distribution():
    """
    Distribute random players in map.
    """

    global MAP
    print(players_dict.keys())
    for player in players_dict.values():
        MAP.player_random_position(player)


def clean_npc(npc):
    if MAP.get_map_matrix(npc.get_position[0], npc.get_position[1]) == str(
        npc.get_level()
    ):
        MAP.set_map_matrix(npc.get_position[0], npc.get_position[1], " ")


def manage_npcs():
    """
    Manage npcs Kafka msgs (keys).
    """

    global npc_dict

    print("[MANAGING NPC] Started managing npc's moves...")

    consumer = KafkaConsumer("npc", bootstrap_servers=KAFKA_SERVER)

    for msg in consumer:
        msg_ = msg.value.decode(FORMAT).split(",")
        npc = NPC(msg_.copy(), MSG=True)
        if msg_[2] not in npc_dict:
            # Only save position first time
            # for engine manage the actual npc position
            npc_dict[npc.get_alias()] = npc
        if not npc_dict[npc.get_alias()].get_dead():
            process_key_npc(npc.get_alias(), msg_[4])
        # else:
        #     clean_npc(npc)


def send_kafka(producer, topic, time, number, message):
    """
    Send msg a number of times by a kafka producer with a time sleep.
    """

    for i in range(0, number):
        producer.send(topic, message.encode(FORMAT))
        sleep(time)


def wait_client():
    while True:
        sleep(1)
        if WAIT_USER is False:
            break


def execute_threads_start_game():
    """
    Thread execution pre-game function.
    """

    global MAP, GAME_STARTED

    GAME_STARTED = True

    # Set weather
    if WEATHER_DICT != {}:
        MAP.set_weather(WEATHER_DICT)
    # Start sending weather
    threading.Thread(target=send_weather, args=()).start()
    # Start sending map
    threading.Thread(target=send_map, args=()).start()
    # Start recieving keys
    threading.Thread(target=recieve_key_clients, args=()).start()
    # Send players kafka
    threading.Thread(target=send_dict_players, args=()).start()
    # Random players distribution
    if RESET == "NO":
        threading.Thread(target=random_player_distribution, args=()).start()
    # Manage NPCs
    threading.Thread(target=manage_npcs, args=()).start()
    # Send npcs kafka
    threading.Thread(target=send_dict_npc, args=()).start()
    # Save state
    threading.Thread(target=save_state_map, args=()).start()
    # See winner
    threading.Thread(target=see_winner, args=()).start()
    ######## P3 ########
    threading.Thread(target=save_map_and_weather_json, args=()).start()


def wait_server():
    """
    Function to wait until game starts.
    """

    global WAIT_USER
    print("[WAIT SERVER] Wait server started. Seconds: {}...".format(TIME_WAIT_SEC))
    producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
    producer.send("wait", "True".encode(FORMAT))
    for i in range(0, TIME_WAIT_SEC):
        producer.send("wait", "True".encode(FORMAT))
        sleep(1)

    WAIT_USER = False
    # Start sending Kafka stop wait
    threading.Thread(target=send_kafka, args=(producer, "wait", 1, 10, "False")).start()

    execute_threads_start_game()


def process_new_position(position, key):
    """
    Gets a key w,a,s,d and return a new position.
    """

    if key == "w":
        return ((position[0] - 1) if position[0] - 1 >= 0 else 19, position[1])
    elif key == "s":
        return ((position[0] + 1) % 20, position[1])
    elif key == "a":
        return (position[0], (position[1] - 1) if position[1] - 1 >= 0 else 19)
    elif key == "d":
        return (position[0], (position[1] + 1) % 20)


def process_key_npc(alias, key):
    """
    Process a key based on a NPC move.
    """

    global MAP, CHANGE, npc_dict, players_dict
    if alias not in npc_dict.keys():
        return False

    npc = npc_dict[alias]
    position = npc.get_position()
    new_position = process_new_position(position, key)
    if position != (-1, -1):
        MAP.evaluate_move_npc(position, new_position, npc, players_dict, npc_dict)
        CHANGE = True
    else:
        npc.set_dead(True)


def process_key_client(alias, key):
    """
    Process a key based on a client player move.
    """

    # TODO procesar ncps enemigos
    global MAP, CHANGE
    if alias not in players_dict.keys():
        return False

    player = players_dict[alias]
    position = MAP.search_player(alias)
    new_position = process_new_position(position, key)
    if not player.get_dead():
        MAP.evaluate_move(position, new_position, player, players_dict, npc_dict)
        CHANGE = True


def recieve_key_clients():
    """
    Recieves keys from clients.
    """

    print("[RECIEVING KEYS] Recieving keys from clients.")
    consumer = KafkaConsumer("keys", bootstrap_servers=KAFKA_SERVER)
    for msg in consumer:
        msg_ = msg.value.decode(FORMAT).split(",")
        alias = msg_[0]
        key = msg_[1]
        process_key_client(alias, key)


def send_dict_npc():
    """
    Send npcs to kafka producer by client.
    """

    producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
    while True:
        sleep(1)
        for key in npc_dict.keys():
            npc = npc_dict[key]
            producer.send(
                "npc_recv",
                dict_sockets()["NPC"]
                .format(
                    alias=npc.get_alias(),
                    level=str(npc.get_level()),
                    position="[{}.{}]".format(
                        str(npc.get_position()[0]), str(npc.get_position()[1])
                    ),
                    key="x",
                    dead=str(npc.get_dead()),
                )
                .encode(FORMAT),
            )


def send_dict_players():
    """
    Send players to kafka producer by client.
    """

    save_dict_players_json()
    producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
    while True:
        sleep(1)
        for key in players_dict.keys():
            player = players_dict[key]
            producer.send(
                "player_{}".format(key[0].lower()),
                dict_sockets()["Player"]
                .format(
                    alias=player.get_alias(),
                    level=str(player.get_level()),
                    hot=str(player.get_hot()),
                    cold=str(player.get_cold()),
                    dead=str(player.get_dead()),
                )
                .encode(FORMAT),
            )


def handle_client(connection, address):
    """
    Handle login and set client on wait mode.
    """

    print("[NEW CONEXION] {} connected.".format(connection))
    alias = login_client(connection, address)

    exchange_keys(alias, connection)

    wait_client()


@DeprecationWarning
def handle_client_old(connection, address):
    """
    Handle client connection to login, start the game and play.
    """

    global CONNECTED, players_dict, RESET_VALUES

    print("[NEW CONEXION] {} connected.".format(connection))

    connected = True
    if not RESET_VALUES:
        RESET_VALUES = True
        reset_values()
    while connected:
        msg = connection.recv(HEADER).decode(FORMAT)
        if msg:
            params_msg = msg.split(",")
            if params_msg[0] == "3":
                player = read_client(params_msg[1], params_msg[2])
                players_dict[player.get_alias()] = player
                if player is not None:
                    print(
                        "[LOGIN] User with IP {} and alias {} have logged in.".format(
                            address[0], player.get_alias()
                        )
                    )
                    connection.send(dict_sockets()["Correct"].encode(FORMAT))
                    connection.send(string_socket_format_player(player).encode(FORMAT))

                    CONNECTED += 1

                    # Waits connection with players
                    if not GAME_STARTED and not WAIT_STARTED:
                        thread_start_game = threading.Thread(
                            target=start_game_server, args=()
                        )
                        thread_start_game.start()

                    # If game not started does nothing with the client
                    while True:
                        if GAME_STARTED:
                            break
                        else:
                            sleep(1)

                    # Resolve the user to play the game
                    if not RESOLVING_USER:
                        thread_send_player = threading.Thread(
                            target=send_player, args=[player.get_alias()]
                        )
                        thread_send_player.start()
                        resolve_user()
                else:
                    print("[LOGIN ERROR] User with IP {} could not login.")
                    connection.send(dict_sockets()["Incorrect"].encode(FORMAT))


def read_cities_json():
    CITIES_JSON = "./json/cities.json"
    if CITIES_JSON is not None:
        with open(CITIES_JSON) as f:
            cities_raw = f.read()
            cities = ast.literal_eval(cities_raw)["cities"]
            return random.sample(cities, 4)
    else:
        return None


def weather_socket():
    global WEATHER_DICT
    WEATHER_DICT = {}
    API_key = "918362daf2a730b6097828f5ad32be49"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    city_names = read_cities_json()
    for city in city_names:
        final_url = base_url + "appid=" + API_key + "&q=" + city
        weather_data = requests.get(final_url).json()
        WEATHER_DICT[city] = round(float(weather_data["main"]["temp"]) - 273.0, 2)
    city_keys = list(WEATHER_DICT.keys())
    print(
        "[CONNECTED WEATHER] Cities choosen: {}({}), {}({}), {}({}), {}({})".format(
            city_keys[0],
            WEATHER_DICT[city_keys[0]],
            city_keys[1],
            WEATHER_DICT[city_keys[1]],
            city_keys[2],
            WEATHER_DICT[city_keys[2]],
            city_keys[3],
            WEATHER_DICT[city_keys[3]],
        )
    )


@DeprecationWarning
def weather_socket_old():
    """
    Process AA_Weather saving 4 cities and they temperatures.
    """

    global WEATHER_DICT
    ADDR = (IP_WEATHER, PUERTO_WEATHER)
    msg = None
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)

        msg = client.recv(2048).decode(FORMAT).split(",")
        print("[CONNECTED WEATHER] Conectado al servidor weather.")
    except ConnectionRefusedError:
        print("[ERROR] Servidor WEATHER no está corriendo...")

    if msg is not None:
        WEATHER_DICT = {
            msg[0]: int(msg[1]),
            msg[2]: int(msg[3]),
            msg[4]: int(msg[5]),
            msg[6]: int(msg[7]),
        }


def server_socket():
    """
    Create a socket listeners for client connections.
    """

    ADDR_SOCKET = (IP_SOCKET, PUERTO_SOCKET)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(ADDR_SOCKET)
    print(
        "[LISTENING] Escuchando AA_Engine Socket Server en {} puerto {}".format(
            IP_SOCKET, PUERTO_SOCKET
        )
    )

    return server_socket


########## MAIN ##########
if len(sys.argv) == 2:
    #     IP = "127.0.0.6"  # puerto de escucha
    #     MAXJUGADORES = 3

    print("[STARTING] Inicializando AA_Engine Socket Server")
    try:
        if RESET == "NO":
            threading.Thread(target=create_map, args=()).start()  # Creamos mapa
        else:
            threading.Thread(target=reset_map, args=()).start()  # Reseteamos estado
        threading.Thread(target=wait_server, args=()).start()
        threading.Thread(target=send_server_active, args=()).start()
        PRIVATE_KEY, _ = create_rsa_key()

        weather_socket()
        server_socket = server_socket()
        server_socket.listen()
        while True:
            conn, addr = server_socket.accept()

            thread_login = threading.Thread(target=handle_client, args=(conn, addr))
            thread_login.start()

        server.close()
    except KeyboardInterrupt:
        print("[POWER OFF] Apagando el servidor...")
    except ConnectionAbortedError:
        print("CONEXION YA EN USO.")
else:
    print("Usage: python3 AA_Engine.py <config.json>")
