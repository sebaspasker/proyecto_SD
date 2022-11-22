import socket
import sqlite3
import sys
import threading
import random
from time import sleep
from src.Map import Map
from src.Player import Player
from src.utils.Sockets_dict import dict_sockets
from src.utils.Sockets_dict import dict_send_error
from src.utils.Process_position import process_position
from kafka import KafkaProducer, KafkaConsumer

FORMAT = "utf-8"
KAFKA_SERVER = "127.0.0.2:9092"
# KAFKA_SERVER = "172.27.203.240:9092"
DB_SERVER = "againstall.db"

IP_SOCKET = "127.0.0.2"
# IP_SOCKET = "172.27.203.240"
PUERTO_SOCKET = 5050
HEADER = 64
FORMAT = "utf-8"

MAX_USERS = 4
CONNECTED = 0
MAP = Map()

GAME_STARTED = False
WAIT_STARTED = False
SENDING_MAP = False
MAP_CREATED = False
MOVE_RECEIVER = False
RESOLVING_USER = False
CHANGE = False
RESET_VALUES = False
WAIT_USER = True

TIME_WAIT_SEC = 20

last_id_msg = {}  # Last id for message client

sys.path.append("src")
sys.path.append("src/exceptions")

players_dict = {}
dead_list = []

###### UTILS ###########
# TODO

# UTILS KAFKA

# UTILS SOCKETS

# UTILS DB

########################


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
    # TODO cambiar
    map_engine.empty_map()

    connection = sqlite3.connect(DB_SERVER)
    cursor = connection.cursor()

    cursor.execute("delete from map_engine;")
    connection.commit()
    save_map(map_engine)

    # Actualiza y mete los jugadores activos en el mapa
    # actualize_players_position()

    # map_p = read_map()
    global MAP
    MAP = read_map()

    connection.commit()
    connection.close()


def save_player_position(connection, cursor, alias, x, y):
    cursor.execute(
        "update players set x = {}, y = {} where alias = '{}'".format(x, y, alias)
    )


def actualize_players_position():
    connection = sqlite3.connect(DB_SERVER)
    cursor = connection.cursor()
    id_rows = cursor.execute("select * from players where active = 1").fetchall()
    map_ = read_map()
    cursor.execute("delete from map_engine;")
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
        "insert into map_engine(map) values('{}')".format(map_to_saved.to_raw_string())
    )

    connection.commit()
    connection.close()


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

        cursor.execute("select * from map_engine order by id desc")

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
    except KeyboardInterrupt:
        print("Keyboard Interruption: Cerrando engine...")


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
    except KeyboardInterrupt:
        print("Keyboard Interruption: Cerrando engine...")


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
                player = Player(player_string, ddbb=True)
                return player
            else:
                print("[WARNING] Player not found.")
    else:
        print("[ERROR] Parameters of client too big.")
    return None


def wait_until_change():
    global CHANGE
    while True:
        if CHANGE:
            return True


def send_map(server=None):
    """
    Sends a map with kafka to 'map_engine' topic.
    """

    global GAME_STARTED
    global SENDING_MAP, CHANGE
    GAME_STARTED = True
    SENDING_MAP = True

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
        except KeyboardInterrupt:
            print("Keyboard Interruption: Cerrando engine...")


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
                if player is not None:
                    player.reset_game()
                    players_dict[player.get_alias()] = player
                    connection.send(dict_sockets()["Correct"].encode(FORMAT))
                    connection.send(string_format_player(player).encode(FORMAT))
                    print(
                        "[LOGIN] User with IP {} and alias {} have logged in.".format(
                            address[0], player.get_alias()
                        )
                    )

                    return player.get_alias()
                else:
                    print("[LOGIN ERROR] User with IP {} could not login.")
                    connection.send(dict_sockets()["Incorrect"].encode(FORMAT))


def random_player_distribution():
    global MAP
    for player in players_dict.values():
        MAP.player_random_position(player)


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


def wait_server():
    global WAIT_USER
    print("[WAIT SERVER] Wait server started. Seconds: {}...".format(TIME_WAIT_SEC))
    producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
    producer.send("wait", "True".encode(FORMAT))
    for i in range(0, TIME_WAIT_SEC):
        producer.send("wait", "True".encode(FORMAT))
        sleep(1)
        if i == 50:
            send_map()
    WAIT_USER = False
    # Start sending Kafa stop wait
    threading.Thread(target=send_kafka, args=(producer, "wait", 1, 10, "False")).start()
    # Start sending map
    threading.Thread(target=send_map, args=()).start()
    # Start recieving keys
    threading.Thread(target=recieve_key_clients, args=()).start()
    random_player_distribution()


def process_new_position(position, key):
    if key == "w":
        return ((position[0] - 1) if position[0] - 1 >= 0 else 19, position[1])
    elif key == "s":
        return ((position[0] + 1) % 20, position[1])
    elif key == "a":
        return (position[0], (position[1] - 1) if position[1] - 1 >= 0 else 19)
    elif key == "d":
        return (position[0], (position[1] + 1) % 20)


def process_key_client(alias, key):
    global MAP, CHANGE
    if alias not in players_dict.keys():
        return False

    player = players_dict[alias]
    position = MAP.search_player(alias)
    new_position = process_new_position(position, key)
    MAP.evaluate_move(position, new_position, player)
    CHANGE = True
    # TODO Crear función empty map, función random player position in map,
    # función distribute players_dict in map random y ver como se mueve vacío


def recieve_key_clients():
    print("[RECIEVING KEYS] Recieving keys from clients.")
    consumer = KafkaConsumer("keys", bootstrap_servers=KAFKA_SERVER)
    for msg in consumer:
        msg_ = msg.value.decode(FORMAT).split(",")
        alias = msg_[0]
        key = msg_[1]
        process_key_client(alias, key)


def send_dict_players():
    while True:
        sleep(1)
        for key in dict_players.keys:
            pass
            # producer.send(bootstrap_servers=KAFKA_SERVER)
            # TODO


def handle_client(connection, address):
    print("[NEW CONEXION] {} connected.".format(connection))
    alias = login_client(connection, address)

    wait_client()

    print("START GAME")


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


def server_socket():
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


# TODO Seguramente en el handle client -> Solo uno acepta los movimientos
# TODO Al moverse no se mueve bien el usuario
# TODO Maps hay veces que no borra el movimiento anterior
# TODO Arreglar engine

########## MAIN ##########
if len(sys.argv) == 1:
    #     IP = "127.0.0.6"  # puerto de escucha
    #     MAXJUGADORES = 3
    #     PUERTO_WEATHER = 8080
    #     ADDR = (IP, PUERTO_WEATHER)

    print("[STARTING] Inicializando AA_Engine Socket Server")

    threading.Thread(target=create_map, args=()).start()  # Creamos mapa
    threading.Thread(target=wait_server, args=()).start()

    server_socket = server_socket()
    server_socket.listen()
    while True:
        conn, addr = server_socket.accept()

        thread_login = threading.Thread(target=handle_client, args=(conn, addr))
        thread_login.start()

    server.close()


#     client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client.connect(
#         ADDR
#     )  # nada mas conectarse con el servidor de clima este hace la select de las 4 ciudades
#     print(f"Establecida conexión en [{ADDR}]")

#     client.close()
# else:
#     print(
#         "Oops!. Parece que algo falló. Necesito estos argumentos: <Puerto de escucha> <Número máximo de jugadores> <Puerto AA_Weather>"
#     )

# start_game()
# read_map()
# send_map(KAFKA_SERVER)
