import socket
from sqlite3.dbapi2 import Error 
import threading
import sys
from typing import List
import sqlite3

FORMAT = 'utf-8'
FIN = "FIN"
HEADER = 64



########## MAIN ##########
if  (len(sys.argv) == 1):
    IP = '127.0.0.1' #puerto de escucha
    MAXJUGADORES = 3
    PUERTO_WEATHER = 8080
    ADDR = (IP, PUERTO_WEATHER)
    
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR) # nada mas conectarse con el servidor de clima este hace la select de las 4 ciudades
    print (f"Establecida conexión en [{ADDR}]")

    # Recibo un string con 4 ciudades aleatorias y sus temperaturas separadas por comas
    msg = client.recv(HEADER).decode(FORMAT)
    lista = msg.split(",")
    
    ciudad1 = (lista[0], lista[1])
    ciudad2 = (lista[2], lista[3])
    ciudad3 = (lista[4], lista[5])
    ciudad4 = (lista[6], lista[7])
    print(ciudad1)


    print(msg)
    # Recibo un mensaje del cliente
    print(f" He recibido del cliente [{ADDR}] el mensaje: {msg}")
    

            
    client.close()
else:
    print ("Oops!. Parece que algo falló. Necesito estos argumentos: <Puerto de escucha> <Número máximo de jugadores> <Puerto AA_Weather>")