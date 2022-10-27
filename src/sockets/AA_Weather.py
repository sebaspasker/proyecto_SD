import socket
from sqlite3.dbapi2 import Error
import threading
import sys
import sqlite3

# Variables globales constantes
HEADER = 64
SERVER = "127.0.0.6"
FORMAT = "utf-8"
FIN = "FIN"


def enviarCiudades(conn, addr):
    # Conexión a la bd
    connection = sqlite3.connect("../../clima.db")

    # Cursor para realizar los comandos de la bd
    cursor = connection.cursor()

    # Comando para extraer 4 ciudades aleatoriamente de la base de datos
    command = "select * from cities order by random() limit 4;"
    cursor.execute(command)

    # Al hacer fetcall en resultado se guardaría una lista de tuplas con las 4 ciudades
    resultado = cursor.fetchall()

    print("Enviadas ciudades")


########## MAIN ##########
if len(sys.argv) == 1:
    PORT = 8080  # sys.argv[1]
    ADDR = (SERVER, int(PORT))

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    print("[STARTING] Inicializando AA_Weather...")
    server.listen()
    print(f"[LISTENING] Servidor a la escucha en {SERVER}")

    while True:
        conn, addr = server.accept()

        thread = threading.Thread(target=enviarCiudades, args=(conn, addr))
        thread.start()
else:
    print("Error en los parámetros: AA_Weather.py <puerto escucha>")
