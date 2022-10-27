from .exceptions.out_of_range_exception import OutOfRangeException
from .exceptions.not_player_exception import NotPlayerException
from .Player import *

# types = {
#     "player" : Player(),
#     "NPC" : NPC(),
# }


def get_city(position):
    if position[0] <= 10 and position[1] <= 10:
        return "Londres"
    elif position <= 20 and position[1] <= 10:
        return "Alicante"
    elif position <= 10 and position[1] <= 20:
        return "Sidney"
    elif position <= 20 and position[1] <= 20:
        return "Wisconsin"
    else:
        raise OutOfRangeException()


class Position:
    position = (0, 0)
    type_m = ""


dict_positions = {
    0: "None",
    1: "Player",
    2: "NPC",
    3: "Mine",
    4: "Food",
}


class Map:
    map_matrix = []
    map_class = []

    def __init__(self):
        self.map_matrix = [[0 for i in range(1, 21)] for j in range(1, 21)]
        self.map_class = [[None for i in range(1, 21)] for j in range(1, 21)]

    def evaluate_position(self, position):
        return self.map_matrix[position[0]][position[1]]

    def evaluate_move(self, old_position, new_position):
        if evaluate_position(old_position) is not "Player":
            raise NotPlayerException("Position should be a player")
        else:
            player = self.map_class[old_position[0]][old_position[1]]

        new_position_class = evaluate_position(new_position)

        if new_position_class is "Player":
            winner player.fight()
