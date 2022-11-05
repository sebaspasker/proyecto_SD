import socket
import sqlite3
import sys
import threading
from time import sleep
from src.Map import Map
from src.Player import Player
from src.utils.Sockets_dict import dict_sockets
from kafka import KafkaProducer, KafkaConsumer

FORMAT = "utf-8"
KAFKA_SERVER = "172.20.40.181:9092"
DB_SERVER = "againstall.db"

# IP_SOCKET = "127.0.0.2"
IP_SOCKET = "172.20.40.181"
PUERTO_SOCKET = 5050

HEADER = 64
FORMAT = "utf-8"

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


def start_game():
    """
    Start a map game and saves it in the ddbb.
    """

    global map_engine
    map_engine = Map()

    connection = sqlite3.connect(DB_SERVER)
    cursor = connection.cursor()

    command = "select * from player_id;"
    id_rows = cursor.execute(command).fetchall()

    map_engine.distribute_ids(id_rows)

    # map_engine.print_color()

    cursor.execute("delete from map_engine;")
    connection.commit()
    cursor.execute(
        "insert into map_engine(map) values('{}')".format(map_engine.to_raw_string())
    )

    connection.commit()
    connection.close()


def start_game_client():
    pass


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


def resolve_user(server):
    pass


def read_client(alias, passwd) -> Player:
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


def handle_client(connection, address):
    print("[NEW CONEXION] {} connected.".format(connection))

    connected = True
    while connected:
        msg_length = connection.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)

            params_msg = msg.split(",")
            if params_msg[0] == "3":
                # TODO Login
                player = read_client(params_msg[1], params_msg[2])
                if player is not None:
                    print(
                        "[LOGIN] User with IP {} and alias {} have logged in.".format(
                            address[0], player.get_alias()
                        )
                    )
                    connection.send(dict_sockets()["Correct"].encode(FORMAT))

                    thread_sendmap = threading.Thread(target=send_map, args=())
                    thread_sendmap.start()
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
    start_game()
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
player = Player()
