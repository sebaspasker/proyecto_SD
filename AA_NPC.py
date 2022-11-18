import sys
from kafka import KafkaProducer
import random
import time
import threading

FORMAT = "utf-8"
KAFKA_SERVER = "127.0.0.2:9092"


movimientos = {0: "w", 1: "s", 2: "a", 3: "d"}

producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
print("NPC activos")

try:
    while True:
        time.sleep(5)
        movimiento = movimientos[random.randint(0, 3)]
        producer.send("npc", (str(movimiento)).encode(FORMAT))
except KeyboardInterrupt:
    print("Cierro npc")
