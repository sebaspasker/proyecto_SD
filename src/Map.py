from blessed import Terminal
from .exceptions.out_of_range_exception import OutOfRangeException
from .exceptions.not_player_exception import NotPlayerException
from .utils.Colors import *
from .utils.Search_player_dict import search_players_dict
from .utils.Replace_string import replace_string, replace_string_reverse
from random import choices, randint
from .Player import *

import sys
import string

# sys.path.append("../")

# types = {
#     "player" : Player(),
#     "NPC" : NPC(),
# }

term = Terminal()


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


dict_positions = {" ": "None", "M": "Mine", "A": "Food"}
for i in range(0, 10):
    dict_positions[str(i)] = "NPC"
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
    weather = None

    def __init__(self, map_string=None):
        if map_string is None:
            self.map_matrix = [
                [
                    " " if randint(0, 10) <= 8 else ["M", "A"][randint(0, 1)]
                    for i in range(0, 20)
                ]
                for j in range(0, 20)
            ]
        else:
            self.raw_string_to_matrix(map_string)
        self.map_class = [[None for i in range(0, 20)] for j in range(0, 20)]

    def __str__(self):
        map_str = "    0   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16  17  18  19\n"

        cities_line_first, cities_line_last = self.last_and_first_weather_lines()
        map_str = cities_line_first + map_str

        for i in range(0, 20):
            if i <= 9:
                map_str += "{}  ".format(i)
            else:
                map_str += "{} ".format(i)

            for j in range(0, 20):
                map_str += " {} |".format(self.map_matrix[i][j])
            map_str += "\n"

        map_str += cities_line_last
        return map_str

    def last_and_first_weather_lines(self):
        cities_line = "                                                                                  \n"

        cities_line_first = replace_string_reverse(
            replace_string(
                cities_line,
                "{} {}º".format(
                    list(self.weather.keys())[0], list(self.weather.values())[0]
                ),
            ),
            "{} {}º".format(
                list(self.weather.keys())[1], list(self.weather.values())[1]
            ),
        )

        cities_line_last = replace_string_reverse(
            replace_string(
                cities_line,
                "{} {}º".format(
                    list(self.weather.keys())[2], list(self.weather.values())[2]
                ),
            ),
            "{} {}º".format(
                list(self.weather.keys())[3], list(self.weather.values())[3]
            ),
        )

        return cities_line_first, cities_line_last

    def search_player(self, alias):
        char = alias[0].lower()
        for i, row in zip(range(len(self.map_matrix)), self.map_matrix):
            if char in row:
                return (i, row.index(char))
        return (-1, -1)

    def empty_map(self):
        self.map_matrix = [[" " for x in range(0, 20)] for i in range(0, 20)]

    def npc_random_position(self, npc):
        while True:
            x, y = randint(0, 19), randint(0, 19)
            if (
                self.evaluate_position((x, y)) != "Player"
                or self.evaluate_position((x, y)) != "NPC"
            ):
                self.map_matrix[x][y] = str(npc.get_level())
                npc.set_position(x, y)
                break

    def player_random_position(self, player):
        while True:
            x, y = randint(0, 19), randint(0, 19)
            if (
                self.evaluate_position((x, y)) != "Player"
                or self.evaluate_position((x, y)) != "NPC"
            ):
                self.map_matrix[x][y] = player.get_alias()[0].lower()
                break

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
            if char >= "a" and char <= "z":
                prYellow(char)
            elif char == "M":
                prRed(char)
            elif char == "A":
                prLightPurple(char)
            else:
                print(char, end="")

    @DeprecationWarning
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

    @DeprecationWarning
    def evaluate_fight_old(self, old_position, new_position, player1, player2):
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

        return winner

    @DeprecationWarning
    def evaluate_mine_old(self, old_position, new_position, player, mine):
        """
        Evaluate if player move to a Mine.
        The player dies.
        """

        player.set_dead(True)
        self.set_map_matrix(old_position[0], old_position[1], " ")
        self.set_map_matrix(new_position[0], new_position[1], " ")
        return player

        # Set map positions
        player.set_position(new_position[0], new_position[1])
        self.set_map_matrix(old_position[0], old_position[1], " ")
        self.set_map_matrix(
            new_position[0], old_position[1], player.get_alias().lower()[0]
        )
        return player
        # self.set_map(old_position[0], old_position[1], 0, None)
        # self.set_map(new_position[0], new_position[1], 1, player)

    @DeprecationWarning
    def evaluate_move_old(self, old_position, new_position, player):

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

    def evaluate_mine(self, old_position, new_position, player):
        """
        Evaluate when a player enters to a mine.
        """
        self.set_map_matrix(old_position[0], old_position[1], " ")
        self.set_map_matrix(new_position[0], new_position[1], " ")
        player.set_dead(True)

    def evaluate_food(self, old_position, new_position, player):
        """
        Evaluate when a player eats a food.
        """
        player.set_level(player.get_level() + 1)
        self.set_map_matrix(old_position[0], old_position[1], " ")
        self.set_map_matrix(
            new_position[0], new_position[1], player.get_alias().lower()[0]
        )

    def evaluate_space_npc(self, old_position, new_position, npc):
        """
        Evaluate when a npc moves to a space, food or mine.
        """
        self.set_map_matrix(old_position[0], old_position[1], " ")
        self.set_map_matrix(new_position[0], new_position[1], str(npc.get_level()))
        npc.set_position(new_position[0], new_position[1])

    def evaluate_space(self, old_position, new_position, player):
        """
        Evaluate when a player moves to a space.
        """
        self.set_map_matrix(old_position[0], old_position[1], " ")
        self.set_map_matrix(
            new_position[0], new_position[1], player.get_alias().lower()[0]
        )

    def sum_weather(self, position, player):
        """
        Returns players cold when a city is under/eq 10º and returns hot
        when a city is over/eq 25º.
        """
        w = None
        if position[0] <= 9 and position[1] <= 9:
            w = list(self.weather.values())[0]
        elif position[0] <= 19 and position[1] <= 9:
            w = list(self.weather.values())[1]
        elif position[0] <= 9 and position[1] <= 19:
            w = list(self.weather.values())[2]
        elif position[0] <= 19 and position[1] <= 19:
            w = list(self.weather.values())[3]

        if w <= 10:
            return player.get_cold()
        elif w >= 25:
            return player.get_hot()
        else:
            return 0
        return w

    def evaluate_fight(self, old_position, new_position, player, players_dict):
        """
        Evaluate a fight between two players. Have in count weather conditions.
        In case P1 level > P2 level = P2 dies and P1 moves to P2 position.
        In case P1 level < P2 level = P1 dies.
        In case P1 level == P2 level = Nothing happens.
        """
        char_player2 = self.get_map_matrix(new_position[0], new_position[1])
        player2 = search_players_dict(char_player2, players_dict)

        w_1 = self.sum_weather(old_position, player)
        w_2 = self.sum_weather(new_position, player2)

        if player.get_level() + w_1 > player2.get_level() + w_2:
            self.set_map_matrix(old_position[0], old_position[1], " ")
            self.set_map_matrix(
                new_position[0], new_position[1], player.get_alias().lower()[0]
            )
            player2.set_dead(True)
        elif player.get_level() + w_1 < player2.get_level() + w_2:
            self.set_map_matrix(old_position[0], old_position[1], " ")
            player.set_dead(True)

    def evaluate_fight_npc(self, old_position, new_position, npc, players_dict):
        """
        Evaluate a fight between a npc and a player (started by the npc movement).
        Have in count P2 weather conditions.
        In case NPC level > P2 level = P2 dies and NPC moves to P2 position.
        In case NPC level < P2 level = NPC dies.
        In case NPC level == P2 level = Nothing happens.
        """
        char_player2 = self.get_map_matrix(new_position[0], new_position[1])
        player2 = search_players_dict(char_player2, players_dict)
        w_2 = self.sum_weather(new_position, player2)

        if npc.get_level() > player2.get_level() + w_2:
            self.set_map_matrix(old_position[0], old_position[1], " ")
            self.set_map_matrix(new_position[0], new_position[1], str(npc.get_level()))
            player2.set_dead(True)
        elif npc.get_level() < player2.get_level() + w_2:
            self.set_map_matrix(old_position[0], old_position[1], " ")
            npc.set_dead(True)

    def evaluate_npc(self, old_position, new_position, player, npc_dict):
        """
        Evaluate a fight between one player and a npc (started by the player).
        help(evaluate_fight_npc) to see conditions.
        """
        npc_fight = None
        for npc in npc_dict.values():
            if npc.get_position() == new_position:
                npc_fight = npc
                break
        if npc_fight is not None:
            w_1 = self.sum_weather(old_position, player)
            if player.get_level() + w_1 > npc_fight.get_level():
                self.set_map_matrix(old_position[0], old_position[1], " ")
                self.set_map_matrix(
                    new_position[0], new_position[1], player.get_alias().lower()[0]
                )
                npc.set_dead(True)
                npc_dict[npc.get_alias] = npc

            elif player.get_level() + w_1 < npc_fight.get_level():
                self.set_map_matrix(old_position[0], old_position[1], " ")
                player.set_dead(True)

    def evaluate_move(self, old_position, new_position, player, players_dict, npc_dict):
        """
        Evaluate a players move.
        """
        new_position_object = self.evaluate_position(new_position)
        if new_position_object == "None":
            self.evaluate_space(old_position, new_position, player)
        elif new_position_object == "Player":
            self.evaluate_fight(old_position, new_position, player, players_dict)
        elif new_position_object == "Food":
            self.evaluate_food(old_position, new_position, player)
        elif new_position_object == "Mine":
            self.evaluate_mine(old_position, new_position, player)
        elif new_position_object == "NPC":
            self.evaluate_npc(old_position, new_position, player, npc_dict)

    def evaluate_move_npc(
        self, old_position, new_position, npc, players_dict, npc_dict
    ):
        """
        Evaluate a npc move.
        """
        new_position_object = self.evaluate_position(new_position)
        if (
            new_position_object == "None"
            or new_position_object == "Food"
            or new_position_object == "Mine"
        ):
            self.evaluate_space_npc(old_position, new_position, npc)
        elif new_position_object == "Player":
            self.evaluate_fight_npc(old_position, new_position, npc, players_dict)

    # SETTERS
    def set_map_matrix(self, x, y, char):
        self.map_matrix[x][y] = char

    def set_player_in_map(self, x, y, player):
        self.set_map_matrix(x, y, player.get_alias()[0].lower())

    def set_npc_in_map(self, x, y, npc):
        npc.set_position(x, y)
        self.set_map_matrix(x, y, str(npc.get_level()))

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

    def set_weather(self, weather_dict):
        self.weather = weather_dict

    # GETTERS
    def get_map_matrix(self, x, y):
        if in_map_range(x, y):
            return self.map_matrix[x][y]

    def get_map_class(self, x, y):
        if in_map_range(x, y):
            return self.map_class[x][y]
        else:
            return None

    def get_weather(self):
        return self.weather

    # TESTING
    def set_none_influencial_weather(self):
        self.weather = {"None1": 15, "None2": 15, "None3": 15, "None4": 15}


# map_class = Map()
# print(map_class)
# player_class = Player()
# oponent_class = Player()

# map_class.set_map(0, 0, 1, player_class)
# map_class.set_map(0, 1, 1, oponent_class)
# map_class.evaluate_move((0, 0), (0, 1))
