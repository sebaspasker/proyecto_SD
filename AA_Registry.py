import socket
from sqlite3.dbapi2 import Error 
import threading
import sys
from typing import List
import sqlite3


# Variables globales constantes
HEADER = 64
SERVER = '127.0.0.3'
FORMAT = 'utf-8'
FIN = "FIN"


# Función para crear un nuevo jugador en la bd
def crearPerfil(lista: List, conn):
    try:
        # Conexión a la bd
        connection = sqlite3.connect('againstall.db')

        # Cursor para realizar los comandos de la bd
        cursor = connection.cursor()

        # Comando para insertar el jugador en la bd
        command = "Insert into players values('" + lista[1] + "', '" + lista[2] + "', 1, 0, 0)"
        cursor.execute(command)

        conn.send("Perfil creado con éxito.".encode(FORMAT))

        # Hago commit para guardar los datos en la bd
        connection.commit()
    except Error as e:
        conn.send("Error".encode(FORMAT))
    finally:
        cursor.close()
        connection.close()



# Función para cambiar la contraseña a un jugador
def editarPerfil(lista: List, conn):
    try:
        # Conexión a la bd
        connection = sqlite3.connect('againstall.db')

        # Cursor para realizar los comandos de la bd
        cursor = connection.cursor()

        # Comando para cambiar la contraseña al jugador
        command = "Update players set pass='" + lista[2] + "' WHERE alias='" + lista[1] + "'"
        cursor.execute(command)
        
        if cursor.rowcount == 0:
            conn.send("No se ha encontrado el alias en la base de datos.".encode(FORMAT))
        else:
            conn.send("Perfil editado con éxito.".encode(FORMAT))

        # Hago commit para guardar los datos en la bd
        connection.commit()

    except Error as e:
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
            
            if lista[0] == '1': 
                if len(lista) == 3:
                    crearPerfil(lista, conn)
                else:
                    conn.send("Error".encode(FORMAT))
            elif lista[0] == '2':
                if len(lista) == 3:
                    editarPerfil(lista, conn)
                else:
                    conn.send("Error".encode(FORMAT))
 
        connected = False
        conn.close()


########## MAIN ##########
if len(sys.argv) == 1:
    PORT = 5050 #sys.argv[1]
    ADDR = (SERVER, int(PORT))

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    print("[STARTING] Inicializando AA_Registry...")
    server.listen()
    print(f"[LISTENING] Servidor a la escucha en {SERVER}")

    while True:
        conn, addr = server.accept()

        thread = threading.Thread(target=handleCliente, args=(conn, addr))
        thread.start()
else:
    print("Error en los parámetros: AA_Registry.py <puerto escucha>")