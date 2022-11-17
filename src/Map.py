from .exceptions.out_of_range_exception import OutOfRangeException
from .exceptions.not_player_exception import NotPlayerException
from .utils.Colors import *
from random import choices, randint
from .Player import *

import sys
import string

# sys.path.append("../")

# types = {
#     "player" : Player(),
#     "NPC" : NPC(),
# }


@DeprecationWarning
def get_city(position):
    if position[0] <= 9 and position[1] <= 9:
        return "Londres"
    elif position <= 19 and position[1] <= 9:
        return "Alicante"
    elif position <= 9 and position[1] <= 19:
        return "Sidney"
    elif position <= 19 and position[1] <= 19:
        return "Wisconsin"
    else:
        raise OutOfRangeException("Range should be between 0 and 19")


class Position:
    position = (0, 0)
    type_m = ""


# TODO Cambiar a jugadores y NPC ids
dict_positions = {" ": "None", "M": "Mine", "F": "Food"}
dict_positions[range(1, 10)] = "NPC"
for char in list(string.ascii_lowercase):
    dict_positions[char] = "Player"


def in_map_range(x, y):
    if x >= 0 and x <= 19 and y >= 0 and y <= 19:
        return True
    else:
        return False


class Map:
    map_matrix = []
    map_class = []

    def __init__(self, map_string=None):
        if map_string is None:
            self.map_matrix = [
                [
                    " " if randint(0, 10) <= 6 else ["M", "F"][randint(0, 1)]
                    for i in range(0, 20)
                ]
                for j in range(0, 20)
            ]
        else:
            self.raw_string_to_matrix(map_string)
        self.map_class = [[None for i in range(0, 20)] for j in range(0, 20)]

    def __str__(self):
        map_str = "    0   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16  17  18  19\n"
        for i in range(0, 20):
            if i <= 9:
                map_str += "{}  ".format(i)
            else:
                map_str += "{} ".format(i)

            for j in range(0, 20):
                map_str += " {} |".format(self.map_matrix[i][j])
            map_str += "\n"

        return map_str

    def raw_string_to_matrix(self, map_string):
        """
        Converts a raw varchar(400) in the map_matrix.
        """
        self.map_matrix = []
        if len(map_string) > 400:
            raise OutOfRangeException("Debería de ser 400 carácteres.")

        j = 0
        row = []
        for i in range(0, 400):
            row.append(map_string[i])
            j += 1
            if j >= 20:
                self.map_matrix.append(row.copy())
                j = 0
                row = []

    def to_raw_string(self):
        """
        Converts the map_matrix to a raw string.
        """
        return_string = ""
        for row in self.map_matrix:
            for x in row:
                return_string += x
        return return_string

    def print_color(self):
        """
        Prints the map_matrix in color.
        """
        map_string = self.__str__()
        for char in map_string:
            if char >= "0" and char <= "9":
                prYellow(char)
            elif char == "M":
                prRed(char)
            elif char == "F":
                prLightPurple(char)
            else:
                print(char, end="")

    def distribute_ids(self, list_ids):
        """
        Distribute the active players ids around the map.

        Input: (player_id, alias, active)
        """

        for id_player, alias, active in list_ids:
            while True:
                x = randint(0, 19)
                y = randint(0, 19)
                if self.get_map_matrix(x, y) == " " and active:
                    break
            self.set_map_matrix(x, y, str(id_player))

    def evaluate_position(self, position):
        """
        Evaluates the matrix position, returning a string of the object
        """
        return dict_positions[self.get_map_matrix(position[0], position[1])]

    def evaluate_fight(self, old_position, new_position, player1, player2):
        """
        Evaluate when player-player or player-NPC fight.
        Case player1 wins:
            player 2 dies and player 1 move to player 2 position.
        Case player2 wins:
            player 1 dies and player 2 stays in position?
        Case same level:
            nothing happens.
        """

        winner = player1.fight(player2)
        if winner == 1:
            # Player who whe fight is dead
            player2.set_dead(True)

            # Change map
            # Set player old position to 0
            self.set_map(old_position[0], old_position[1], 0, None)

            # Move player
            player.set_position(new_position[0], new_position[1])
            self.set_map(new_position[0], new_position[1], 1, player)

            # TODO Gestionamos en la base de datos
            # TODO Gestionamos con sockets
        elif winner == 2:
            # Kills player
            player.set_dead(True)

            # Change map and kill player
            self.set_map(old_position[0], old_position[1], 0, None)

            # TODO Gestionamos en la base de datos
            # TODO Gestionamos en sockets
            # TODO Gestionamos la muerte del player

        return winner

    def evaluate_mine(self, old_position, new_position, player, mine):
        """
        Evaluate if player move to a Mine.
        The player dies.
        """

        player.set_dead(True)
        self.set_map_matrix(old_position[0], old_position[1], " ")
        self.set_map_matrix(new_position[0], new_position[1], " ")

    def evaluate_food(self, old_position, new_position, player, food):
        if player.get_level() < 10:
            player.set_level(player.get_level() + 1)

        # Set map positions
        player.set_position(new_position[0], new_position[1])
        self.set_map_matrix(old_position[0], old_position[1], " ")
        self.set_map_matrix(
            new_position[0], old_position[1], player.get_alias().lower()[0]
        )
        return player
        # self.set_map(old_position[0], old_position[1], 0, None)
        # self.set_map(new_position[0], new_position[1], 1, player)

    def evaluate_move(self, old_position, new_position, player):

        # Evaluate what is in the new position
        new_position_class = self.evaluate_position(new_position)

        # If in the new position there is a player or NPC,
        # they fight
        if new_position_class == "Player" or new_position_class == "NPC":
            # TODO Detectar nivel jugador y en base a eso eliminar al otro o no
            # self.evaluate_fight(old_position, new_position, player, new_position_class)
            pass
        elif new_position_class == "Mine":
            player = self.evaluate_mine(
                old_position, new_position, player, new_position_class
            )
        elif new_position_class == "Food":
            player = self.evaluate_food(
                old_position, new_position, player, new_position_class
            )
        elif new_position_class == "None":
            # Moves player
            player.set_position(new_position[0], new_position[1])
            self.set_map_matrix(old_position[0], old_position[1], " ")
            self.set_map_matrix(
                new_position[0], new_position[1], player.get_alias().lower()[0]
            )

        return player

        # if get_city(old_position) != get_city(new_position):
        # TODO
        # Mirar la temperatura del servidor de temperatura y evaluar en base a
        # ello el jugador
        # pass

        # print(self.get_map_matrix)

    # SETTERS
    def set_map_matrix(self, x, y, char):
        self.map_matrix[x][y] = char

    @DeprecationWarning
    def set_map_class(self, x, y, obj):
        if in_map_range(x, y):
            self.map_class[x][y] = obj
        else:
            raise OutOfRangeException("Range should be between 0 and 19")

    @DeprecationWarning
    def set_map(self, x, y, num, obj):
        """
        Change map Matrix of numbers and change map Matrix of objects
        """

        self.set_map_matrix(x, y, num)
        self.set_map_class(x, y, obj)

    # GETTERS
    def get_map_matrix(self, x, y):
        if in_map_range(x, y):
            return self.map_matrix[x][y]
        else:
            raise OutOfRangeException("Range should be between 0 and 19")

    def get_map_class(self, x, y):
        if in_map_range(x, y):
            return self.map_class[x][y]
        else:
            raise OutOfRangeException("Range should be between 0 and 19")


# map_class = Map()
# print(map_class)
# player_class = Player()
# oponent_class = Player()

# map_class.set_map(0, 0, 1, player_class)
# map_class.set_map(0, 1, 1, oponent_class)
# map_class.evaluate_move((0, 0), (0, 1))
