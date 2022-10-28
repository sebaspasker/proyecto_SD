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


def send(msg, client):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)


def enviarCiudades(ip, puerto):
    ADDR = (ip, int(puerto))

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print("[STARTING] AA_WEATHER inicializándose...")
    print(f"[LISTENING] AA_WEATHER a la escucha en {SERVER}")

    while True:
        conn, addr = server.accept()

        try:
            # Conexión a la bd
            connection = sqlite3.connect("clima.db")

            # Cursor para realizar los comandos de la bd
            cursor = connection.cursor()

            # Comando para extraer 4 ciudades aleatoriamente de la base de datos
            command = "select * from cities order by random() limit 4;"
            cursor.execute(command)

            # Al hacer fetcall en resultado se guardaría una lista de tuplas con las 4 ciudades
            resultado = cursor.fetchall()

            cadena = ""
            for ciudad in resultado:
                cadena += str(ciudad[0]) + "," + str(ciudad[1]) + ","
        except Error as e:
            print("Algo falló")
        finally:
            cursor.close()
            connection.close()

        conn.send(str(cadena).encode(FORMAT))
        conn.close()

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

    # server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server.bind(ADDR)

    # print("[STARTING] Inicializando AA_Weather...")
    # server.listen()
    # print(f"[LISTENING] Servidor a la escucha en {SERVER}")

    # conn, addr = server.accept()

    thread = threading.Thread(target=enviarCiudades, args=(SERVER, int(PORT)))

    thread.start()
else:
    print("Error en los parámetros: AA_Weather.py <puerto escucha>")
