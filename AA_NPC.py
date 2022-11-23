import random
import time
import threading
import sys
from kafka import KafkaProducer
from src.utils.Sockets_dict import dict_sockets

FORMAT = "utf-8"
KAFKA_SERVER = "127.0.0.2:9092"
NUMBER_NPC = 3
npc_dict = {}


moves = {0: "w", 1: "s", 2: "a", 3: "d"}


def create_npc(id_):
    npc = NPC()
    npc.create_random(id_)
    npc_dict[npc.get_alias()] = npc
    return npc


def send_move_npc(alias):
    move = moves[randint(0, 3)]


####### MAIN #######
for x in range(1, NUMBER_NPC + 1):
    npc = create_npc(x)
    thread_send_move_npc = threading.Thread(target=send_move_npc, args=[npc.get_alias])
    print(
        "[CREATED NPC] Created NPC with alias {} and level {}".format(
            npc.get_alias(), npc.get_level()
        )
    )
