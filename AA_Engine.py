import socket
import sqlite3
import sys
from src.Map import Map
from kafka import KafkaProducer, KafkaConsumer


sys.path.append("src")
sys.path.append("src/exceptions")


def start_game():
    map_engine = Map()

    connection = sqlite3.connect("againstall.db")
    cursor = connection.cursor()

    command = "select * from player_id;"
    id_rows = cursor.execute(command).fetchall()

    map_engine.distribute_ids(id_rows)

    map_engine.print_color()


def send_map(server):
    try:
        producer = KafkaProducer(bootstrap_server=server)
        consumer = KafkaConsumer("map_actualization", server)
    except ValueError as VE:
        print("VALUE ERROR: Cerrando engine...")
        print("{}".format(VE.message))
    except KeyboardInterrupt:
        print("Keyboard Interruption: Cerrando engine...")


########## MAIN ##########
# if len(sys.argv) == 1:
#     IP = "127.0.0.6"  # puerto de escucha
#     MAXJUGADORES = 3
#     PUERTO_WEATHER = 8080
#     ADDR = (IP, PUERTO_WEATHER)

#     client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client.connect(
#         ADDR
#     )  # nada mas conectarse con el servidor de clima este hace la select de las 4 ciudades
#     print(f"Establecida conexión en [{ADDR}]")

#     client.close()
# else:
#     print(
#         "Oops!. Parece que algo falló. Necesito estos argumentos: <Puerto de escucha> <Número máximo de jugadores> <Puerto AA_Weather>"
#     )

start_game()
