import socket
import sqlite3
import sys
import threading
from time import sleep
from src.Map import Map
from src.Player import Player
from src.utils.Sockets_dict import dict_sockets
from src.utils.Process_position import process_position
from kafka import KafkaProducer, KafkaConsumer

FORMAT = "utf-8"
KAFKA_SERVER = "127.0.0.2:9092"
DB_SERVER = "againstall.db"

# IP_SOCKET = "127.0.0.2"
IP_SOCKET = "127.0.0.2"
PUERTO_SOCKET = 5050

HEADER = 64
FORMAT = "utf-8"

MAX_USERS = 4
CONNECTED = 0

GAME_STARTED = False
WAIT_STARTED = False
SENDING_MAP = False
MAP_CREATED = False
MOVE_RECEIVER = False

TIME_WAIT_SEC = 20

last_id_msg = {}  # Last id for message client

sys.path.append("src")
sys.path.append("src/exceptions")


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


def create_map():
    """
    Create a map game and saves it in the ddbb.
    """

    print("[CREATING MAP] Creating the map and saving in the ddbb.")

    global map_engine
    map_engine = Map()

    connection = sqlite3.connect(DB_SERVER)
    cursor = connection.cursor()

    command = "select * from player_id;"
    id_rows = cursor.execute(command).fetchall()

    # map_engine.distribute_ids(id_rows)

    # map_engine.print_color()

    cursor.execute("delete from map_engine;")
    connection.commit()
    cursor.execute(
        "insert into map_engine(map) values('{}')".format(map_engine.to_raw_string())
    )

    connection.commit()
    connection.close()
    global MAP_CREATED
    MAP_CREATED = True


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

    if MAP_CREATED is not False:
        thread_create_map = threading.Thread(target=create_map, args=())
        thread_create_map.start()

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

        cursor.execute("select * from map_engine")

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

    except ValuerError as VE:
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
                player = Player(player_string)
                return player
            else:
                print("[WARNING] Player not found.")
    else:
        print("[ERROR] Parameters of client too big.")
    return None


def send_map(server=None):
    """
    Sends a map with kafka to 'map_engine' topic.
    """

    global GAME_STARTED
    global SENDING_MAP
    GAME_STARTED = True
    SENDING_MAP = True

    if server is None:
        producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
    else:
        producer = KafkaProducer(bootstrap_servers=server)

    print("[SENDING MAP] Sending map raw char to topic '{}'".format("map_engine"))

    while True:
        map_read = read_map()

        try:
            producer.send("map_engine", bytes(map_read.to_raw_string(), "utf-8"))
            sleep(2)
        except ValueError as VE:
            print("VALUE ERROR: Cerrando engine...")
            print("{}".format(VE.message))
        except KeyboardInterrupt:
            print("Keyboard Interruption: Cerrando engine...")


def process_key(key, position_, player):
    act_map = read_map()
    position = process_position(position_)
    new_position = see_new_position(position, key)
    print("IN")


def process_client_msg(msgs, player):
    global last_id_msg

    Alias = player.get_alias()[0]

    for msg_ in msgs[-5:]:  # Separated msgs by spaces
        msg = msg_.split(",")  # Separate msg by comma
        if msg[0] != "6":
            pass
        if int(msg[3]) <= last_id_msg[Alias]:
            pass
        key = msg[1]
        position = msg[2]  # Different format
        process_key(key, position, player)


def resolve_user(player, kafka_server=None):
    global last_id_msg
    global MOVE_RECEIVER

    last_id_msg[player.get_alias()[0]] = 0

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
            "read_user_move_{}".format(player.get_alias()[0]),
            bootstrap_servers=KAFKA_SERVER,
        )
        for msg in consumer:
            msg_split = msg.value.dedode(FORMAT).split(" ")
            thread_process_client_msg = threading.Thread(
                target=process_client_msg, args=(msg_split, player)
            )
            thread_process_client_msg.start()


def handle_client(connection, address):
    """
    Handle client connection to login, start the game and play.
    """

    global CONNECTED

    print("[NEW CONEXION] {} connected.".format(connection))

    connected = True
    while connected:
        msg_length = connection.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)

            params_msg = msg.split(",")
            if params_msg[0] == "3":
                player = read_client(params_msg[1], params_msg[2])
                if player is not None:
                    print(
                        "[LOGIN] User with IP {} and alias {} have logged in.".format(
                            address[0], player.get_alias()
                        )
                    )
                    connection.send(dict_sockets()["Correct"].encode(FORMAT))

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
                    resolve_user(player)
                else:
                    print("[LOGIN ERROR] User with IP {} could not login.")
                    connection.send(dict_sockets()["Incorrect"].encode(FORMAT))


# TODO Empezar partida para que cuando pase un timeout aunque solo sea un jugador o cuando hay un máximo de jugadores
# TODO La partida termina cuando solo queda uno
# TODO Nos ha dado error en el puerto de kafka - Revisar puertos antes de ejecutar en el labaratorio.

########## MAIN ##########
if len(sys.argv) == 1:
    #     IP = "127.0.0.6"  # puerto de escucha
    #     MAXJUGADORES = 3
    #     PUERTO_WEATHER = 8080
    #     ADDR = (IP, PUERTO_WEATHER)
    ADDR_SOCKET = (IP_SOCKET, PUERTO_SOCKET)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(ADDR_SOCKET)
    print("[STARTING] Inicializando AA_Engine Socket Server")
    server_socket.listen()
    print(
        "[LISTENING] Escuchando AA_Engine Socket Server en {} puerto {}".format(
            IP_SOCKET, PUERTO_SOCKET
        )
    )

    while True:
        conn, addr = server_socket.accept()

        thread_login = threading.Thread(target=handle_client, args=(conn, addr))
        print(KAFKA_SERVER)
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
