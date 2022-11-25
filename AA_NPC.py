import json
import random
import sys
import threading
import time
from kafka import KafkaProducer, KafkaConsumer
from random import randint
from src.utils.Sockets_dict import dict_sockets
from src.NPC import NPC
from time import sleep

if len(sys.argv) == 2:
    with open(sys.argv[1]) as f:
        JSON_CFG = json.load(f)
    KAFKA_SERVER = JSON_CFG["KAFKA_SERVER"]
    NUMBER_NPC = JSON_CFG["NUMBER_NPC"]
    FORMAT = JSON_CFG["FORMAT"]

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


def recieve_npcs():
    global npc_bool, npc_dict
    kafka_consumer = KafkaConsumer("npc_recv", bootstrap_servers=KAFKA_SERVER)
    for msg in kafka_consumer:
        msg_ = msg.value.decode(FORMAT).split(",")
        npc = NPC(msg_, True)

        if msg_[5] == "True":
            npc.set_dead(True)
        else:
            npc.set_dead(False)

        npc_bool[npc.get_alias()] = True
        if not npc_dict[npc.get_alias()].get_dead():
            npc_dict[npc.get_alias()] = npc

    print("[END RECIEVE] Stopping recieving moves")


def send_move_npc(alias):
    global npc_dict, npc_bool
    producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
    while True:
        if npc_dict[alias].get_dead():
            break

        sleep(2)
        npc = npc_dict[alias]
        move = moves[randint(0, 3)]
        producer.send(
            "npc",
            dict_sockets()["NPC"]
            .format(
                alias=npc.get_alias(),
                level=npc.get_level(),  # DEPRECATED (NOT USING)
                position="({}.{})".format(  # DEPRECATED (NOT USING)
                    str(npc.get_position()[0]), str(npc.get_position()[1])
                ),
                key=move,
                dead="x",
            )
            .encode(FORMAT),
        )

        npc_bool[alias] = False

    print("[NCP DEAD] NPC alias {} ha muerto.".format(alias))


####### MAIN #######
if len(sys.argv) == 2:
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

    # Recieve npcs from Engine
    thread_recieve_npcs = threading.Thread(target=recieve_npcs, args=())
    thread_recieve_npcs.start()
else:
    print("Usage: python AA_NPC.py <config.json>")
