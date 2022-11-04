from getpass import getpass
from time import sleep
from kafka import KafkaProducer, KafkaConsumer
from src.Map import Map
from src.utils.Sockets_dict import dict_sockets
from src.utils.Clear import clear
import socket
import sys

HEADER = 64
PORT = 5050
KAFKA_SERVER = "localhost:9092"
FORMAT = "utf-8"
FIN = "FIN"


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


def login(client):
    """
    Function for user login inside the MMO game.
    """

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
    if msg[1] == "1":
        print("Logueado correctamente al servidor.")
        play_game()
    else:
        print("No se ha podido loguear al servidor.")


def play_game():
    """
    Function to return the map and play the game
    """

    kafka_consumer = KafkaConsumer("map_engine", bootstrap_servers=KAFKA_SERVER)
    kafka_producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
    for message in kafka_consumer:
        # print(len(message.value.decode(FORMAT)[-1]))
        print(message.value.decode(FORMAT)[-400:])
        map_player = Map(message.value.decode(FORMAT)[-400:])
        clear()
        print("Selecciona arriba/izquierda/derecha/abajo: (w/a/s/d)")
        map_player.print_color()
        sleep(1)


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
        elif opcion == "4":
            break

    client.close()
else:
    print(
        "Oops!. Parece que algo falló. Necesito estos argumentos: <ServerIP> <Puerto>"
    )
