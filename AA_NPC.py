import random
import time
import threading
import sys
from random import randint
from src.utils.Sockets_dict import dict_sockets
from src.NPC import NPC
from time import sleep
from kafka import KafkaProducer

FORMAT = "utf-8"
KAFKA_SERVER = "127.0.0.2:9092"
NUMBER_NPC = 5
npc_dict = {}
npc_bool = {}


moves = {0: "w", 1: "s", 2: "a", 3: "d"}


def create_npc(id_):
    global npc_dict
    npc = NPC()
    npc.create_random(id_)
    npc_dict[npc.get_alias()] = npc
    npc_bool[npc.get_alias()] = True
    return npc


def recieve_move_npc(alias):
    pass


def recieve_npcs():
    kafka_consumer = KafkaConsumer("npc_recv", bootstrap_servers=KAFKA_SERVER)
    for msg in kafka_consumer:
        msg_ = msg.value.decode(FORMAT).split(",")
        # TODO Hacer que reciba el mensaje, actualice el npc,
        # y lo meta en la lista de npc bool si ha habido cambio


def send_move_npc(alias):
    global npc_dict
    producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
    while True:
        while npc_bool[npc.get_alias()]:
            # Espera a cambio para seguir moviendose
            sleep(1)
        npc = npc_dict[alias]
        move = moves[randint(0, 3)]
        producer.send(
            "npc",
            dict_sockets()["NPC"]
            .format(
                alias=npc.get_alias(),
                level=npc.get_level(),
                position="({}.{})".format(
                    str(npc.get_position()[0]), str(npc.get_position()[1])
                ),
                key=move,
            )
            .encode(FORMAT),
        )


####### MAIN #######
for x in range(1, NUMBER_NPC + 1):
    npc = create_npc(x)
    thread_send_move_npc = threading.Thread(
        target=send_move_npc, args=[npc.get_alias()]
    )
    thread_send_move_npc.start()
    print(
        "[CREATED NPC] Created NPC with alias {} and level {}".format(
            npc.get_alias(), npc.get_level()
        )
    )
