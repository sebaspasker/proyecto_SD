import json
import logging
import threading
import socket
import sqlite3
import sys
from typing import List
from sqlite3.dbapi2 import Error
from src.utils.assymetric_encryption import *

logging.basicConfig(
    filename="./logs/sockets_registry.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(clientip)s - %(message)s",
)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if len(sys.argv) == 2:
    with open(sys.argv[1]) as f:
        JSON_CFG = json.load(f)
    # Variables globales constantes
    HEADER = JSON_CFG["HEADER"]
    SERVER = JSON_CFG["IP_REG"]
    PORT = JSON_CFG["PORT_REG"]
    FORMAT = JSON_CFG["FORMAT"]
    DB_SERVER = JSON_CFG["DB_SERVER"]

PRIVATE_KEY = None
PUBLIC_KEY = None

# Función para crear un nuevo jugador en la bd
def crearPerfil(lista: List, conn, addr, public_key_cli):
    try:
        logger.info(
            "Creación de perfil, alias: {}".format(lista[1]),
            extra={"clientip": addr},
        )
        # Conexión a la bd
        connection = sqlite3.connect(DB_SERVER)

        # Cursor para realizar los comandos de la bd
        cursor = connection.cursor()

        # Comando para insertar el jugador en la bd
        command = (
            "Insert into players values("
            + "'{}',".format(lista[1])
            + "'{}',".format(lista[2])
            + "1, 0, 0, 0, 0)"
        )
        cursor.execute(command)

        send_encrypted_message(public_key_cli, "Perfil creado con exito", conn)

        # Hago commit para guardar los datos en la bd
        connection.commit()
        print("Perfil creado con éxito.")
        logger.info(
            "Perfil creado con éxito, alias: {}".format(lista[1]),
            extra={"clientip": addr},
        )
    except Error as e:
        print("ERROR: No se ha podido añadir el usuario")
        logger.error(
            "No se ha podido añadir el usuario con alias: {}".format(lista[1]),
            extra={"clientip": addr},
        )
        send_encrypted_message(public_key_cli, "Error", conn)
    finally:
        cursor.close()
        connection.close()


# Función para cambiar la contraseña a un jugador
def editarPerfil(lista: List, conn, addr, public_key_cli):
    try:
        logger.info(
            "Edición de perfil, alias: {}".format(lista[1]),
            extra={"clientip": addr},
        )
        # Conexión a la bd
        connection = sqlite3.connect(DB_SERVER)

        # Cursor para realizar los comandos de la bd
        cursor = connection.cursor()

        # Comando para cambiar la contraseña al jugador
        command = (
            "Update players set pass='" + lista[2] + "' WHERE alias='" + lista[1] + "'"
        )
        cursor.execute(command)

        if cursor.rowcount == 0:
            send_encrypted_message(public_key_cli, "ALIAS_NOT_FOUND", conn)
            # conn.send("ALIAS_NOT_FOUND".encode(FORMAT))
        else:
            send_encrypted_message(public_key_cli, "Perfil editado con éxito.", conn)
            # conn.send("Perfil editado con éxito.".encode(FORMAT))
            logger.info(
                "Perfil editado con éxito, alias: {}".format(lista[1]),
                extra={"clientip": addr},
            )

        # Hago commit para guardar los datos en la bd
        connection.commit()

    except Error as e:
        logger.error(
            "No se ha podido editar el usuario con alias: {}".format(lista[1]),
            extra={"clientip": addr},
        )
        # conn.send("Error".encode(FORMAT))
        send_encrypted_message(public_key_cli, "Error", conn)
    finally:
        cursor.close()
        connection.close()


# Función para manejar el mensaje del cliente que se conecta
def handleCliente(conn, addr):
    print(f"[NUEVA CONEXION] {addr} connected.")

    private_key_host, public_key_host = create_rsa_key()
    conn.send(get_public_key_bytes(public_key_host))  # Envía clave pública

    public_key_cli = read_public_key_bytes(conn.recv(512))
    # length = int(conn.recv(HEADER).decode(FORMAT))
    # msg_rsa = conn.recv(256)
    # msg_rsa_1 = conn.recv(256)
    # msg_rsa_2 = conn.recv(256)
    # msg_rsa_3 = conn.recv(256)
    # # print(length)
    # map_ = (
    #     decrypt(private_key, msg_rsa).decode("utf-8")
    #     + decrypt(private_key, msg_rsa_1).decode("utf-8")
    #     + decrypt(private_key, msg_rsa_2).decode("utf-8")
    #     + decrypt(private_key, msg_rsa_3).decode("utf-8")
    # )

    # print(len(map_))

    # map__ = Map(map_)

    # map__.set_none_influencial_weather()
    # map__.print_color()

    connected = True
    while connected:
        # msg_length = conn.recv(HEADER).decode(FORMAT)
        # if msg_length:
        # msg_length = int(msg_length)
        # msg = conn.recv(msg_length).decode(FORMAT)
        msg = decrypt_recieved_message(private_key_host, conn)

        # Recibo un mensaje del cliente
        print(f" He recibido del cliente [{addr}] el mensaje: {msg}")

        # Lo separo en una lista para poder usarlo más fácilmente
        lista = msg.split(",")

        if lista[0] == "1":
            if len(lista) == 3:
                crearPerfil(lista, conn, addr, public_key_cli)
            else:
                send_encrypted_message(public_key_cli, "Error", conn)
        elif lista[0] == "2":
            if len(lista) == 3:
                editarPerfil(lista, conn, addr, public_key_cli)
            else:
                send_encrypted_message(public_key_cli, "Error", conn)

        connected = False
        conn.close()


########## MAIN ##########
if len(sys.argv) == 2:
    ADDR = (SERVER, int(PORT))

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(ADDR)

        print("[STARTING] Inicializando AA_Registry...")
        server.listen()
        print(f"[LISTENING] Servidor a la escucha en {SERVER}")

        while True:
            conn, addr = server.accept()

            thread = threading.Thread(target=handleCliente, args=(conn, addr))
            thread.start()
    except KeyboardInterrupt:
        print("[POWER OFF] Apagando Servidor AA_Registry...")
else:
    print("Usage: python AA_Registry.py <config.json>")
