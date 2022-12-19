import blessed
from getpass import getpass
from time import sleep, time
from kafka import KafkaProducer, KafkaConsumer
from src.exceptions.socket_exception import SocketException
from src.Map import Map
from src.Player import Player
from src.Map import Map
from src.utils.Sockets_dict import dict_sockets
from src.utils.Clear import clear
from src.utils.Process_position import position_str
from src.utils.assymetric_encryption import read_public_key_bytes, encrypt
import ast
import json
import urllib3
import threading
import requests
import socket
import sys
from waiting import wait

term = blessed.Terminal()

# Deshabilitamos Warnings
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if len(sys.argv) == 2:
    with open(sys.argv[1]) as f:
        JSON_CFG = json.load(f)
    IP_ENGINE = JSON_CFG["IP_ENGINE"]
    PORT_ENGINE = JSON_CFG["PORT_ENGINE"]
    IP_REG = JSON_CFG["IP_REG"]
    PORT_REG = JSON_CFG["PORT_REG"]
    KAFKA_SERVER = JSON_CFG["KAFKA_SERVER"]
    FORMAT = JSON_CFG["FORMAT"]

# GLOBAL VARIABLES
PLAYER = Player()
MAP = None
WEATHER = None

# GLOBAL BOOLS
GAME_STARTED = False
GAME_END = False
SERVER_ON = True
CHANGE = False
EXIT = False
EXIT_ALL = False
WINNER = False


def reset_values():
    global PLAYER, MAP, WEATHER
    global GAME_STARTED, GAME_END, EXIT, SERVER_ON, CHANGE, WINNER
    PLAYER = Player()
    MAP = None
    WEATHER = None

    GAME_STARTED = False
    GAME_END = False
    EXIT = False
    SERVER_ON = True
    CHANGE = False
    WINNER = False


########## UPDATE P3 #########
def get_user_api():
    """
    Obtiene un usuario mediante API.
    """

    try:
        requests.get("https://localhost:8080/registry", verify=False)

        print("Obtención de usuario mediante API.")

        print("Introduzca alias:")
        alias = input()
        response = requests.get(
            "https://localhost:8080/registry/{}".format(alias), verify=False
        )

        if response.status_code == 200:
            json_user = response.json()
            print(
                "\nUsuario {alias}:\nLEVEL:{level}\nCOLD:{cold}\nHOT:{hot}\nDEAD:{dead}\n\n".format(
                    alias=json_user["alias"],
                    level=json_user["level"],
                    cold=json_user["cold"],
                    hot=json_user["hot"],
                    dead=json_user["dead"],
                )
            )
        elif response.status_code == 400:
            print("No existe el usuario.")
        else:
            print("No se ha podido obtener al usuario.")

    except Exception as e:
        print("Servidor API no conectado.")
        raise e


def create_user_api():
    """
    Crea un usuario mediante API.
    """
    # Comprobamos estado del servidor
    try:
        response = requests.get("https://localhost:8080/registry", verify=False)

        print("Creación de usuario por api:")
        print("Introduzca alias:")
        alias = input()
        passwd = getpass(prompt="Contraseña:")
        if (
            requests.get(
                "https://localhost:8080/registry/{}".format(alias), verify=False
            ).status_code
            == 404
        ):
            response = requests.post(
                "https://localhost:8080/registry",
                data={"alias": alias, "password": passwd},
                verify=False,
            )
            print("Usuario creado con exito.")
        else:
            print("Ya existe el usuario")
    except Exception as e:
        print("ERROR - API Server not connected. Connect server.")


def edit_user_api():
    """
    Modifica un usuario mediante API.
    """
    try:
        response = requests.get("https://localhost:8080/registry", verify=False)

        print("Edición de usuario por api:")
        print("Introduzca alias:")
        alias = input()
        passwd = getpass(prompt="Nueva contraseña:")
        if (
            requests.get(
                "https://localhost:8080/registry/{}".format(alias), verify=False
            ).status_code
            == 200
        ):
            if (
                requests.put(
                    "https://localhost:8080/registry/{}".format(alias),
                    data={"password": passwd},
                    verify=False,
                ).status_code
                != 200
            ):
                print("ERROR - No se ha podido modificar el usuario")
            else:
                print("Usuario editado con éxito.")
        else:
            print("ERROR - Usuario no encontrado.")

    except Exception as e:
        print("API Server not connected. Connect server.")


def delete_user_api():
    """
    Elimina un usuario mediante API.
    """

    try:
        response = requests.get("https://localhost:8080/registry", verify=False)

        print("Eliminar usuario:")
        print("Introduzca alias:")

        alias = input()
        if (
            requests.get(
                "https://localhost:8080/registry/{}".format(alias), verify=False
            ).status_code
            == 200
        ):
            status = requests.delete(
                "https://localhost:8080/registry/{}".format(alias), verify=False
            ).status_code
            if status != 200:
                print("Usuario no se ha podido eliminar..")
            else:
                print("Usuario eliminado con exito.")
        else:
            print("No existe el usuario.")
    except Exception as e:
        print("API Server not connected.")


#############################

# TODO Encriptar sockets

# Función para enviar mensajes cliente
def send(msg, client):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b" " * (64 - len(send_length))
    client.send(send_length)
    client.send(message)


def send_rsa(msg, client):
    message = msg
    # msg_length = len(message)
    # send_length = msg_length
    # client.send(str(send_length).encode(FORMAT) + b" " * (64 - len(str(send_length))))
    client.send(message)


def menu():
    print("Elige una opción:")
    print("1. Crear perfil")
    print("2. Editar perfil")
    print("3. Unirse a la partida")
    print("4. Crear perfil API")
    print("5. Editar perfil API")
    print("6. Borrar perfil API")
    print("7. Obtener usuario API")
    print("8. Unirse a la partida API")
    print("9. Salir")
    print("Opción: ", end=" ")


def create_user(IP, PORT):
    # Conexion
    ADDR = (IP, int(PORT))

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
    except ConnectionRefusedError:
        print(
            "ERROR: No se ha podido conectar a AA_Registry IP:{}, PUERTO:{}. Seguro que está corriendo?\n\n".format(
                IP, PORT
            )
        )
        return False

    print(f"CONEXIÓN ESTABLECIDA [{ADDR}]")

    import src.Map

    public_key_msg = client.recv(2048)  # RSA
    public_key = read_public_key_bytes(public_key_msg)
    # map_ = Map().to_raw_string()
    # print(len(map_))
    # msg = encrypt(public_key, map_[0:100])
    # msg_1 = encrypt(public_key, map_[100:200])
    # msg_2 = encrypt(public_key, map_[200:300])
    # msg_3 = encrypt(public_key, map_[300:400])
    # print(
    #     len(map_[0:100]) + len(map_[100:200]) + len(map_[200:300]) + len(map_[300:400])
    # )
    # send_rsa(bytearray(msg), client)
    # send_rsa(bytearray(msg_1), client)
    # send_rsa(bytearray(msg_2), client)
    # send_rsa(bytearray(msg_3), client)

    print("Opción de creación de usuario")
    print("Introduzca alias:", end=" ")
    alias = input()

    while True:
        password = getpass(prompt="Contraseña:")

        password2 = getpass(prompt="Repita la contraseña:")
        if password2 == password:
            break
        else:
            print("NO COINCIDEN LAS CONTRASEÑAS")

    # Envío al servidor toda la información necesaria en forma de mensaje
    # El 1 simboliza que la sentencia de SQL a realizar es insert
    send("1," + alias + "," + password, client)

    if client.recv(2048).decode(FORMAT) == "Error":
        print("ERROR: No se ha podido añadir el usuario.")

    client.close()


def edit_user(IP, PORT):
    ADDR = (IP, int(PORT))
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
    except ConnectionRefusedError:
        print(
            "ERROR: No se ha podido conectar a AA_Registry IP:{}, PUERTO:{}. Seguro que está corriendo?\n\n".format(
                IP, PORT
            )
        )
        return False

    private_key = client.recv(2048).decode(FORMAT)
    print(private_key)

    print("Opción de edición de usuario:")
    print("Alias: ", end=" ")
    alias = input()
    password = getpass(prompt="Nueva contraseña:")

    send("2," + alias + "," + password, client)
    msg = client.recv(2048).decode(FORMAT)

    if msg == "ALIAS_NOT_FOUND":
        print("ERROR: No se ha podido encontrar el usuario en la base de datos.")
    elif msg == "ERROR":
        print("ERROR: No se ha podido editar el usuario.")
    else:
        print(msg)

    client.close()


def process_player(msg):
    msg_split = msg.split(",")
    if msg_split[0] != "7":
        raise SocketException("Incorrect socket message should be 7")
    msg_split.pop(0)
    player = Player(msg_split)
    return player


def login(IP, PORT):
    """
    Function for user login inside the MMO game.
    """
    global PLAYER

    engine_addr = (IP, int(PORT))
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(engine_addr)
    except ConnectionRefusedError:
        print(
            "ERROR: No se ha podido conectar a AA_Engine. Seguro que está corriendo?\n"
        )
        return False

    print("Opcion de login, introduzca los siguientes datos para empezar el juego:")
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
    consumer = KafkaConsumer(
        "wait", bootstrap_servers=KAFKA_SERVER, consumer_timeout_ms=3000
    )
    timer = time()
    for msg in consumer:
        if msg.value.decode(FORMAT) == "False":
            return True
        else:
            clear()
            print(wait_text.format(abs(int(timer - time()))))
    return False


def start_game():
    all_correct = wait_user()

    if all_correct:

        thread_read_weather_cli = threading.Thread(target=read_weather_cli, args=())
        thread_read_weather_cli.start()

        thread_read_map_cli = threading.Thread(target=read_map_cli, args=())
        thread_read_map_cli.start()

        thread_read_player_cli = threading.Thread(target=read_player_cli, args=())
        thread_read_player_cli.start()

        thread_send_move_cli = threading.Thread(target=send_move_cli, args=())
        thread_send_move_cli.start()

        thread_print_game = threading.Thread(target=print_game, args=())
        thread_print_game.start()

        thread_read_winner_cli = threading.Thread(target=read_winner_cli, args=())
        thread_read_winner_cli.start()

        while not EXIT and SERVER_ON:
            sleep(1)
    else:
        return False


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


def winner():
    dead_msg = []
    dead_msg.append("********************************************************\n")
    dead_msg.append("*************                      *********************\n")
    dead_msg.append("************* ******************** *********************\n")
    dead_msg.append("************* *****   !!   ******* *********************\n")
    dead_msg.append("************* ***** WINNER ******* *********************\n")
    dead_msg.append("************* ******************** *********************\n")
    dead_msg.append("*************                      *********************\n")
    dead_msg.append("********************************************************\n")
    dead_msg.append("                EXIT? Press q                           \n")

    dead_msg_copy = dead_msg.copy()

    while True:
        for i in range(0, 8):
            line = dead_msg[i]
            for x in range(len(line) - 1):
                sleep(0.05)
                if line[x + 1] != "\n":
                    dead_msg_copy[i] = line[:x] + "_" + line[x + 1 :]
                clear()
                print("".join(x for x in dead_msg_copy))
                if EXIT:
                    break
            if EXIT:
                break
        if EXIT:
            break


def dead():
    dead_msg = []
    dead_msg.append("--------------------------------------------------------\n")
    dead_msg.append("-------------                      ---------------------\n")
    dead_msg.append("------------- -------------------- ---------------------\n")
    dead_msg.append("------------- -----   HA   ------- ---------------------\n")
    dead_msg.append("------------- ----- MUERTO ------- ---------------------\n")
    dead_msg.append("------------- -------------------- ---------------------\n")
    dead_msg.append("-------------                      ---------------------\n")
    dead_msg.append("--------------------------------------------------------\n")
    dead_msg.append("                EXIT? Press q                           \n")

    dead_msg_copy = dead_msg.copy()

    while True:
        for i in range(0, 8):
            line = dead_msg[i]
            for x in range(len(line) - 1):
                sleep(0.05)
                if line[x + 1] != "\n":
                    dead_msg_copy[i] = line[:x] + "_" + line[x + 1 :]
                clear()
                print("".join(x for x in dead_msg_copy))
                if EXIT:
                    break
            if EXIT:
                break
        if EXIT:
            break


def print_game():
    """
    Function to print the game client.
    """
    global MAP, PLAYER, CHANGE

    while True:
        if (
            PLAYER.get_dead() is True
            or SERVER_ON is False
            or GAME_END is True
            or WINNER is True
        ):
            break
        if CHANGE:
            clear()
            if MAP is not None:
                MAP.print_color()
            if PLAYER is not None:
                PLAYER.print_interface()
            CHANGE = not CHANGE
    if PLAYER.get_dead():
        dead()
    if WINNER:
        winner()


def read_winner_cli():
    """
    Function to read the winner of the game.
    """
    global WINNER
    consumer = KafkaConsumer(
        "winner_{}".format(PLAYER.get_alias()[0].lower()),
        bootstrap_servers=KAFKA_SERVER,
        consumer_timeout_ms=3000,
    )

    while True:
        for msg in consumer:
            msg_ = msg.value.decode(FORMAT)
            if msg_ == "1":
                WINNER = True
        if EXIT or SERVER_ON is False or GAME_END:
            break


def read_weather_cli():
    """
    Function to read the weather and save it in MAP
    """
    global WEATHER

    consumer = KafkaConsumer(
        "weather", bootstrap_servers=KAFKA_SERVER, consumer_timeout_ms=3000
    )
    for msg in consumer:
        if PLAYER.get_dead() is True or SERVER_ON is False or GAME_END is True:
            break
        msg_ = msg.value.decode(FORMAT).split(",")
        weather = {}
        for i in range(1, 9, 2):
            weather[msg_[i]] = msg_[i + 1]
        WEATHER = weather


def read_map_cli():
    """
    Function to read and print a map
    """

    global MAP, CHANGE

    kafka_consumer = KafkaConsumer(
        "map_engine", bootstrap_servers=KAFKA_SERVER, consumer_timeout_ms=3000
    )

    for message in kafka_consumer:
        if PLAYER.get_dead() is True or SERVER_ON is False or GAME_END is True:
            break
        MAP = Map(message.value.decode(FORMAT)[-400:])
        if WEATHER is None:
            MAP.set_none_influencial_weather()
        else:
            MAP.set_weather(WEATHER)
        CHANGE = True


def send_move_cli():
    """
    Function to get input and send it
    """
    global PLAYER, EXIT, GAME_END

    kafka_producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

    with term.cbreak():
        val = ""
        while val.lower() != "q":
            key = term.inkey()
            if PLAYER.get_dead() is False:
                if key == "w" or key == "s" or key == "a" or key == "d":
                    kafka_producer.send(
                        "keys",
                        "{alias},{key}".format(
                            alias=PLAYER.get_alias(), key=key
                        ).encode(FORMAT),
                    )
            elif not SERVER_ON or EXIT:
                break
            if key == "q":
                GAME_END = True
                break

        EXIT = True


def read_server_cli():
    global GAME_STARTED, TIMESERVER

    try:
        consumer = KafkaConsumer(
            "server", bootstrap_servers=KAFKA_SERVER, consumer_timeout_ms=3000
        )
        while True:
            for msg in consumer:
                SERVER_ON = True
                msg_ = msg.value.decode(FORMAT).split(",")
                if msg_[0] == "2":
                    GAME_STARTED = True
                TIMESERVER = float(msg_[1])
            SERVER_ON = False
            if EXIT_ALL is True:
                break
    except Exception as e:
        print(
            "\n\nEl Servidor de KAFKA seguramente no esté corriendo. Algunas funcionalidades de la aplicación no funcionarán.\n"
        )


def read_player_cli():
    """
    Function to recieve player information
    """
    global PLAYER, CHANGE

    kafka_consumer = KafkaConsumer(
        "player_{}".format(PLAYER.get_alias().lower()[0]),
        bootstrap_servers=KAFKA_SERVER,
        consumer_timeout_ms=2500,
    )

    for msg in kafka_consumer:
        msg_split = msg.value.decode(FORMAT).split(",")
        msg_split.pop(0)
        PLAYER = Player(msg_split)
        CHANGE = True
        if PLAYER.get_dead() is True or SERVER_ON is False:
            break


@DeprecationWarning
def comprobe_dead():
    global PLAYER, DEAD
    sleep(10)
    while True:
        if PLAYER.get_dead() is True:
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
if len(sys.argv) == 2:
    wait_error = True  # Es del revés i know
    threading.Thread(target=read_server_cli, args=()).start()
    opcion = -1
    while opcion != 4:
        reset_values()
        menu()
        opcion = input()

        if opcion == "1":
            clear()
            create_user(IP_REG, PORT_REG)
        elif opcion == "2":
            clear()
            edit_user(IP_REG, PORT_REG)
        elif opcion == "3":
            if not GAME_STARTED:
                clear()
                wait_error = login(IP_ENGINE, PORT_ENGINE)
            else:
                clear()
                print("ERROR: Partida iniciada.")
            if not SERVER_ON or not wait_error:
                print(
                    "ERROR: El servidor AA_Engine se ha caido, probar de nuevo mas tarde..."
                )
            if GAME_END:
                clear()
                print("Partida terminada... Te esperamos de nuevo!")
        elif opcion == "4":
            clear()
            create_user_api()
        elif opcion == "5":
            clear()
            edit_user_api()
        elif opcion == "6":
            clear()
            delete_user_api()
        elif opcion == "7":
            clear()
            get_user_api()
        elif opcion == "9":
            EXIT_ALL = True
            break

else:
    print("Usage: python AA_Player.py <config.json>")
