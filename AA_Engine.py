import socket
import sqlite3
import sys
from src.Map import Map
from kafka import KafkaProducer, KafkaConsumer

FORMAT = "utf-8"
KAFKA_SERVER = "localhost:9092"
DB_SERVER = "againstall.db"

IP_SOCKET = "127.0.0.2"
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
        return sqlite3.connect(DB_SERVER).cursor()
    else:
        return sqlite3.connect(name).cursor()


def start_game():
    """
    Start a map game and saves it in the ddbb.
    """

    global map_engine
    map_engine = Map()

    connection = sqlite3.connect("againstall.db")
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


def read_map(ddbb_server=None):
    """
    Reads the map in the ddbb and saves it in map_read variable.
    """

    global map_read
    try:
        cursor = connect_db(DB_SERVER)

        cursor.execute("select * from map_engine")

        map_str = cursor.fetchone()[1]

        map_read = Map(map_str)

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

        print(map_rec)
    except ValuerError as VE:
        print("VALUE ERROR: Cerrando engine...")
        print("{}".format(VE.message))
    except KeyboardInterrupt:
        print("Keyboard Interruption: Cerrando engine...")


def resolve_user(server):
    pass


def send_map(server):
    """
    Sends a map with kafka to 'map_engine' topic.
    """

    global map_read
    try:
        producer = KafkaProducer(bootstrap_servers=server)

        producer.send("map_engine", bytes(map_read.to_raw_string(), "utf-8"))
    except ValueError as VE:
        print("VALUE ERROR: Cerrando engine...")
        print("{}".format(VE.message))
    except KeyboardInterrupt:
        print("Keyboard Interruption: Cerrando engine...")


def handle_client(connection, address):
    print("[NEW CONEXION] {} connected.".format(connection))

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)


########## MAIN ##########
if len(sys.argv) == 1:
    #     IP = "127.0.0.6"  # puerto de escucha
    #     MAXJUGADORES = 3
    #     PUERTO_WEATHER = 8080
    #     ADDR = (IP, PUERTO_WEATHER)
    ADDR_SOCKET = (IP_SOCKET, PUERTO_SOCKET)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(ADDR_CLIENT)
    print("[STARTING] Inicializando AA_Engine Socket Server")
    server_socket.listen()
    print("[LISTENING] Escuchando AA_Engine Socket Server en {}".format(IP_SOCKET))

    while True:
        conn, addr = server.accept()

        thread = threading.Thread()


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
