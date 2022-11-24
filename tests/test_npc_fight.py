import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.Map import Map
from src.Player import Player
from src.NPC import NPC


def setup():
    MAP = Map()
    player = Player()
    npc = NPC()
    MAP.set_none_influencial_weather()

    player.set_alias("Juan")
    player.set_level(0)
    player.set_dead(False)

    npc.set_alias("NPC_1")
    npc.set_level(0)
    npc.set_dead(False)

    player_dict = {player.get_alias(): player}
    npc_dict = {npc.get_alias(): npc}
    return MAP, player, npc, npc_dict, player_dict


def test_1():
    MAP, player, npc, npc_dict, player_dict = setup()

    position_1 = (0, 1)
    position_2 = (0, 0)

    npc.set_level(1)
    player.set_level(0)

    MAP.set_player_in_map(position_1[0], position_1[1], player)
    MAP.set_npc_in_map(position_2[0], position_2[1], npc)

    MAP.evaluate_move_npc(position_2, position_1, npc, player_dict, npc_dict)

    assert MAP.get_map_matrix(position_1[0], position_1[1]) == "1"
    assert MAP.get_map_matrix(position_2[0], position_2[1]) == " "


def test_2():
    MAP, player, npc, npc_dict, player_dict = setup()

    position_1 = (0, 1)
    position_2 = (0, 0)

    npc.set_level(0)
    player.set_level(1)

    MAP.set_player_in_map(position_1[0], position_1[1], player)
    MAP.set_npc_in_map(position_2[0], position_2[1], npc)

    MAP.evaluate_move_npc(position_2, position_1, npc, player_dict, npc_dict)

    assert MAP.get_map_matrix(position_1[0], position_1[1]) == "j"
    assert MAP.get_map_matrix(position_2[0], position_2[1]) == " "


def test_3():
    MAP, player, npc, npc_dict, player_dict = setup()

    position_1 = (0, 1)
    position_2 = (0, 0)

    npc.set_level(1)
    player.set_level(0)

    MAP.set_player_in_map(position_1[0], position_1[1], player)
    MAP.set_npc_in_map(position_2[0], position_2[1], npc)

    MAP.evaluate_move(position_1, position_2, player, player_dict, npc_dict)

    assert MAP.get_map_matrix(position_2[0], position_2[1]) == "1", "{}".format(
        MAP.get_map_matrix(position_2[0], position_2[1])
    )
    assert MAP.get_map_matrix(position_1[0], position_1[1]) == " "


def test_4():
    MAP, player, npc, npc_dict, player_dict = setup()

    position_1 = (0, 1)
    position_2 = (0, 0)

    npc.set_level(0)
    player.set_level(1)

    MAP.set_player_in_map(position_1[0], position_1[1], player)
    MAP.set_npc_in_map(position_2[0], position_2[1], npc)

    MAP.evaluate_move(position_1, position_2, player, player_dict, npc_dict)

    assert MAP.get_map_matrix(position_1[0], position_1[1]) == " "
    assert MAP.get_map_matrix(position_2[0], position_2[1]) == "j"


def test_5():
    MAP, player, npc, npc_dict, player_dict = setup()

    position_1 = (0, 1)
    position_2 = (0, 0)

    npc.set_level(0)
    player.set_level(0)

    MAP.set_player_in_map(position_1[0], position_1[1], player)
    MAP.set_npc_in_map(position_2[0], position_2[1], npc)

    MAP.evaluate_move(position_1, position_2, player, player_dict, npc_dict)

    assert MAP.get_map_matrix(position_2[0], position_2[1]) == "0", "{}".format(
        MAP.get_map_matrix(position_2[0], position_2[1])
    )

    assert MAP.get_map_matrix(position_1[0], position_1[1]) == "j"


def test_6():
    MAP, player, npc, npc_dict, player_dict = setup()

    position_1 = (0, 1)
    position_2 = (0, 0)

    npc.set_level(0)
    player.set_level(0)

    MAP.set_player_in_map(position_1[0], position_1[1], player)
    MAP.set_npc_in_map(position_2[0], position_2[1], npc)

    MAP.evaluate_move_npc(position_2, position_1, npc, player_dict, npc_dict)

    assert MAP.get_map_matrix(position_2[0], position_2[1]) == "0"
    assert MAP.get_map_matrix(position_1[0], position_1[1]) == "j"


runable_tests = [test_1, test_2, test_3, test_4, test_5, test_6]

for i in range(len(runable_tests)):
    runable_tests[i]()
