import blessed
from getpass import getpass
from time import sleep
from time import time
from kafka import KafkaProducer, KafkaConsumer
from src.exceptions.socket_exception import SocketException
from src.Map import Map
from src.Player import Player
from src.utils.Sockets_dict import dict_sockets
from src.utils.Clear import clear
from src.utils.Process_position import position_str
import threading
import socket
import sys
from waiting import wait

term = blessed.Terminal()

HEADER = 64
PORT = 5050
KAFKA_SERVER = "localhost:9092"
FORMAT = "utf-8"
FIN = "FIN"
LOGIN_ID = -1

PLAYER = Player()
MOVE_ID = 1

DEAD = False
GAME_STARTED = False
GAME_END = False


# Función para enviar mensajes cliente
def send(msg, client):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)


def menu():
    print("Elige una opción:")
    print("1. Crear perfil")
    print("2. Editar perfil")
    print("3. Unirse a la partida")
    print("4. Salir del juego")
    print("Opción: ", end=" ")


def crearPerfil(ip, puerto):
    iguales = False

    # Establezco la conexión
    ADDR = (ip, int(puerto))
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"Establecida conexión en [{ADDR}]")

    print(
        "Has accedido al menu de creación de perfiles, introduce los siguientes datos para continuar: "
    )
    print("Alias que te identifique dentro del juego: ", end=" ")
    alias = input()

    while not iguales:
        print("Contraseña: ", end=" ")
        password = input()

        print("Repita la contraseña: ", end=" ")
        password2 = input()
        if password2 == password:
            iguales = True
        else:
            print("No coinciden las contraseñas")

    # Envío al servidor toda la información necesaria en forma de mensaje
    # El 1 simboliza que la sentencia de SQL a realizar es insert
    send("1," + alias + "," + password, client)

    print(client.recv(2048).decode(FORMAT))

    if client.recv(2048).decode(FORMAT) == "Error":
        return

    client.close()


def editarPerfil(ip, puerto):
    # Establezco la conexión
    ADDR = (ip, int(puerto))
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    print(
        "Has accedido al menu de edición de perfiles, introduce los siguientes datos para cambiar tu contraseña: "
    )
    print("Alias del perfil a editar: ", end=" ")
    alias = input()
    print("Nueva password: ", end=" ")
    password = input()

    # Envío al servidor toda la información necesaria en forma de mensaje
    # El 2 simboliza que la sentencia de SQL a realizar es update
    send("2," + alias + "," + password, client)

    print(client.recv(2048).decode(FORMAT))

    if client.recv(2048).decode(FORMAT) == "Error":
        return

    client.close()


def process_player(msg):
    msg_split = msg.split(",")
    if msg_split[0] != "7":
        raise SocketException("Incorrect socket message should be 7")
    msg_split.pop(0)
    player = Player(msg_split)
    # player.set_position(int(msg_split[1]), int(msg_split[2]))
    # player.set_alias(msg_split[3])
    # player.set_level(int(msg_split[4]))
    # player.set_hot(int(msg_split[5]))
    # player.set_cold(int(msg_split[6]))
    # player.set_dead(bool(msg_split[7]))
    return player


def login(client):
    """
    Function for user login inside the MMO game.
    """
    global PLAYER

    # engine_addr = (engine_ip, int(engine_port))
    # client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client.connect(engine_addr)

    print(
        "Bienvenido, a continuación va a proceder a loguearse. Introduzca los siguientes datos..."
    )
    print("Alias:")
    alias = input()

    passwd = getpass()

    send(dict_sockets()["Login"].format(alias=alias, password=passwd), client)

    msg_rcv = client.recv(2048).decode(FORMAT)
    msg = msg_rcv.split(",")
    if msg[0] == "4":
        if msg[1] == "1":
            print("Logueado correctamente al servidor.")
            ply_sck = client.recv(2048).decode(FORMAT)
            PLAYER = process_player(ply_sck)
            start_game()
    elif msg[0] == "-1":
        print(msg[1])
    else:
        print("Could not connect to the server.")


def wait_user():
    """
    Handle user wait.
    """
    wait_text = "Please, wait until another clients connect...\nSeconds waiting... {}"
    consumer = KafkaConsumer("wait", bootstrap_servers=KAFKA_SERVER)
    timer = time()
    for msg in consumer:
        if msg.value.decode(FORMAT) == "False":
            return True
        else:
            clear()
            print(wait_text.format(abs(int(timer - time()))))


def start_game():
    wait_user()

    thread_read_map_cli = threading.Thread(target=read_map_cli, args=())
    thread_read_map_cli.start()

    # thread_read_player_cli = threading.Thread(target=read_player_cli, args=())
    # thread_read_player_cli.start()

    thread_send_move_cli = threading.Thread(target=send_move_cli, args=())
    thread_send_move_cli.start()

    while not GAME_END:
        sleep(1)


@DeprecationWarning
def start_game_old(server_kafka):
    wait_text = "Please, wait until another clients connect...\n Conected users: {}"
    consumer = (
        KafkaConsumer("start_game", bootstrap_servers=KAFKA_SERVER)
        if server_kafka is None
        else KafkaConsumer("start_game", bootstrap_servers=server_kafka)
    )

    for message in consumer:
        msg_split = message.value.decode(FORMAT).split(",")
        if msg_split[-3:][1] == "Waiting":
            clear()
            print(wait_text.format(msg_split[2]))
        elif msg_split[-3:][1] == "Start":
            clear()
            print("Waiting to response...")
        elif msg_split[-3:][1] == "Start_Game":
            clear()
            print("GAME STARTS WITH {} USERS".format(msg_split[-3:][2]))
            thread_read_player_cli = threading.Thread(target=read_player_cli, args=())
            thread_read_player_cli.start()
            sleep(3)
            play_game()


def dead():
    while True:
        sleep(2)
        clear()
        print("--------------------------------------------------------")
        print("-------------                      ---------------------")
        print("------------- -------------------- ---------------------")
        print("------------- -----   HA   ------- ---------------------")
        print("------------- ----- MUERTO ------- ---------------------")
        print("------------- -------------------- ---------------------")
        print("-------------                      ---------------------")
        print("--------------------------------------------------------")


def read_map_cli():
    """
    Function to read and print a map
    """

    kafka_consumer = KafkaConsumer("map_engine", bootstrap_servers=KAFKA_SERVER)

    for message in kafka_consumer:
        map_player = Map(message.value.decode(FORMAT)[-400:])
        clear()
        map_player.print_color()


def send_move_cli():
    """
    Function to get input and send it
    """
    global PLAYER, MOVE_ID

    kafka_producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

    with term.cbreak():
        val = ""
        while val.lower() != "q":
            # key = input().lower()  # TODO Cambiar a tecla estática
            key = term.inkey()
            if key == "w" or key == "s" or key == "a" or key == "d":
                kafka_producer.send(
                    "keys",
                    "{alias},{key}".format(alias=PLAYER.get_alias(), key=key).encode(
                        FORMAT
                    ),
                )


def read_player_cli():
    """
    Function to recieve player information
    """
    global PLAYER, MOVE_ID

    kafka_consumer = KafkaConsumer(
        "player_{}".format(PLAYER.get_alias().lower()[0]),
        bootstrap_servers=KAFKA_SERVER,
    )

    for msg in kafka_consumer:
        msg_split = msg.value.decode(FORMAT).split(",")
        msg_split.pop(0)
        PLAYER = Player(msg_split)


def comprobe_dead():
    global PLAYER, DEAD
    sleep(10)
    while True:
        if PLAYER.get_dead():
            DEAD = True
            dead()
            break


@DeprecationWarning
def play_game():
    """
    Function to return the map and play the game
    """
    GAME_STARTED = True
    # thread_read_map_cli = threading.Thread(target=read_map_cli, args=())
    # thread_read_map_cli.start()

    thread_send_move_cli = threading.Thread(target=send_move_cli, args=())
    thread_send_move_cli.start()

    thread_comprobe_dead = threading.Thread(target=comprobe_dead, args=())
    thread_comprobe_dead.start()

    read_map_cli()


########## MAIN ##########
if len(sys.argv) == 3:
    IP = sys.argv[1]
    PUERTO = int(sys.argv[2])
    ADDR = (IP, PORT)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"Establecida conexión en [{ADDR}]")

    opcion = -1
    while opcion != 4:
        menu()
        opcion = input()

        if opcion == "1":
            try:
                crearPerfil(IP, PUERTO)
            except ConnectionRefusedError:
                print(
                    "En este momento no se pueden crear perfiles, intentelo de nuevo mas tarde"
                )
        elif opcion == "2":
            try:
                editarPerfil(IP, PUERTO)
            except ConnectionRefusedError:
                print(
                    "En este momento no se pueden editar perfiles, intentelo de nuevo mas tarde"
                )
        elif opcion == "3":
            clear()
            login(client)
            # LOGIN_ID = -1
        elif opcion == "4":
            break

    client.close()
else:
    print(
        "Oops!. Parece que algo falló. Necesito estos argumentos: <ServerIP> <Puerto>"
    )
