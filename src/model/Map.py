from .exceptions.out_of_range_exception import OutOfRangeException
from .exceptions.not_player_exception import NotPlayerException
from .Player import *

# types = {
#     "player" : Player(),
#     "NPC" : NPC(),
# }


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


dict_positions = {
    0: "None",
    1: "Player",
    2: "NPC",
    3: "Mine",
    4: "Food",
}


def in_map_range(x, y):
    if x >= 0 and x <= 19 and y >= 0 and y <= 19:
        return True
    else:
        return False


class Map:
    map_matrix = []
    map_class = []

    def __init__(self):
        self.map_matrix = [[0 for i in range(0, 20)] for j in range(0, 20)]
        self.map_class = [[None for i in range(0, 20)] for j in range(0, 20)]

    def evaluate_position(self, position):
        """
        Evaluates the matrix position, returning a string of the object
        """
        return dict_position(self.get_map_matrix(position[0], position[1]))

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

        winner = player.fight()
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
        self.set_map(old_position[0], old_position[1], 0, None)

        # TODO Gestionamos en la base de datos
        # TODO Gestionamos en sockets

    def evaluate_food(self, old_position, new_position, player, food):
        player.set_level(player.get_level() + 1)

        # Set map positions
        player.set_position(new_position[0], new_position[1])
        self.set_map(old_position[0], old_position[1], 0, None)
        self.set_map(new_position[0], new_position[1], 1, player)

    def evaluate_move(self, old_position, new_position):
        # TODO test
        # See if old position is a player
        if evaluate_position(old_position) is not "Player":
            raise NotPlayerException("Position should be a player")
        else:
            player = self.get_map_class(old_position[0], old_position[1])

        # Evaluate what is in the new position
        new_position_class = evaluate_position(new_position)

        # If in the new position there is a player or NPC,
        # they fight
        if new_position_class is "Player" or new_position_class is "NPC":
            # TODO Test
            self.evaluate_fight(old_position, new_position, player, new_position_class)
        elif new_position_class is "Mine":
            self.evaluate_mine(old_position, new_position, player, new_position_class)
        elif new_position_class is "Food":
            self.evaluate_food(old_position, new_position, player, new_position_class)
        elif new_position_class is "None":
            # Moves player
            player.set_position(new_position[0], new_position[1])
            self.set_map(old_position[0], old_position[1], 0, None)
            self.set_map(new_position[0], new_position[1], 1, player)

        if get_city(old_position) is not get_city(new_position):
            # TODO
            # Mirar la temperatura del servidor de temperatura y evaluar en base a
            # ello el jugador
            pass

    # SETTERS
    def set_map_matrix(self, x, y, num):
        if in_map_range(x, y) and num >= 0 and num <= 4:
            self.map_matrix[x][y] = num
        else:
            raise OutOfRangeException("Range should be between 0 and 19")

    def set_map_class(self, x, y, obj):
        if in_map_range(x, y):
            self.map_class[x][y] = obj
        else:
            raise OutOfRangeException("Range should be between 0 and 19")

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
