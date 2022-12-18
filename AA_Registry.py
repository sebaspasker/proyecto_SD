import json
import logging
import threading
import socket
import sqlite3
import sys
from typing import List
from sqlite3.dbapi2 import Error

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

# Función para crear un nuevo jugador en la bd
def crearPerfil(lista: List, conn, addr):
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

        conn.send("Perfil creado con éxito.".encode(FORMAT))

        # Hago commit para guardar los datos en la bd
        connection.commit()
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
        conn.send("Error".encode(FORMAT))
    finally:
        cursor.close()
        connection.close()


# Función para cambiar la contraseña a un jugador
def editarPerfil(lista: List, conn, addr):
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
            conn.send("ALIAS_NOT_FOUND".encode(FORMAT))
        else:
            conn.send("Perfil editado con éxito.".encode(FORMAT))
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
        conn.send("Error".encode(FORMAT))
    finally:
        cursor.close()
        connection.close()


# Función para manejar el mensaje del cliente que se conecta
def handleCliente(conn, addr):
    print(f"[NUEVA CONEXION] {addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)

            # Recibo un mensaje del cliente
            print(f" He recibido del cliente [{addr}] el mensaje: {msg}")

            # Lo separo en una lista para poder usarlo más fácilmente
            lista = msg.split(",")

            if lista[0] == "1":
                if len(lista) == 3:
                    crearPerfil(lista, conn, addr)
                else:
                    conn.send("Error".encode(FORMAT))
            elif lista[0] == "2":
                if len(lista) == 3:
                    editarPerfil(lista, conn, addr)
                else:
                    conn.send("Error".encode(FORMAT))

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
