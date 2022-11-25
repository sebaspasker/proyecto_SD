import json
import socket
from sqlite3.dbapi2 import Error
import sqlite3
import sys
import threading

if len(sys.argv) == 2:
    with open(sys.argv[1]) as f:
        JSON_CFG = json.load(f)
    # Variables globales constantes
    SERVER = JSON_CFG["IP_WEATHER"]
    PORT = JSON_CFG["PORT_WEATHER"]
    FORMAT = JSON_CFG["FORMAT"]
    HEADER = JSON_CFG["HEADER"]


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
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(ADDR)
    server.listen()
    print("[STARTING] AA_WEATHER inicializándose...")
    print(f"[LISTENING] AA_WEATHER a la escucha en {SERVER}")

    while True:
        try:
            conn, addr = server.accept()
            cadena = ""

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
            print(e)
        except KeyboardInterrupt:
            print("[POWEROFF] Apagando el servidor AA_Weather.")
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
if len(sys.argv) == 2:
    ADDR = (SERVER, int(PORT))

    try:
        thread = threading.Thread(target=enviarCiudades, args=(SERVER, int(PORT)))
        thread.start()
    except KeyboardInterrupt:
        print("[POWEROFF] Apagando el servidor AA_Weather.")

else:
    print("Usage: python AA_Weather.py <config.json>")
