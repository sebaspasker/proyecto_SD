from .exceptions.none_value_exception import NoneValueException
from .exceptions.incorrect_format import IncorrectFormatException
from .exceptions.out_of_range_exception import OutOfRangeException
from random import randint
import hashlib
import sys

sys.path.append("../")


def fight(player_1, player_2):
    """
    Fight between two players, wins the player who have more level.
    1: Win Player1
    2: Win Player2
    0: No one wins
    """

    if player_1.get_level() > player_2.get_level():
        return 1
    elif player_1.get_level() < player_2.get_level():
        return 2
    else:
        return 0


class Player:
    # position = (1, 1)
    alias = ""
    password = ""
    level = 0
    cold = 0
    hot = 0
    dead = False

    def __init__(self, string_list=None, ddbb=False):
        # TODO Cambiar para que añada el password
        if string_list is not None:
            if not ddbb:
                self.set_alias(string_list[0])
                self.set_level(int(string_list[1]))
                self.set_hot(int(string_list[2]))
                self.set_cold(int(string_list[3]))
                if string_list[4] == "False":
                    self.set_dead(False)
                elif string_list[4] == "True":
                    self.set_dead(True)
            else:
                self.set_alias(string_list[0])
                self.set_level(int(string_list[3]))
                self.set_cold(int(string_list[4]))
                self.set_hot(int(string_list[5]))
                self.set_dead(bool(string_list[6]))

    def __str__(self):
        return (
            "Player alias: {}\n".format(self.set_alias)
            + "-----------------\n"
            # + "Position: {}\n".format(self.get_position())
            + "Level: {}\n".format(self.get_level())
            + "Cold: {}\n".format(self.get_cold())
            + "Hot: {}\n".format(self.get_hot())
            + "Dead: {}\n".format(self.get_dead())
            + "-----------------\n"
        )

    def print_interface(self):
        alias_ = "".join(self.get_alias()[0:9]) + "".join(
            "_" for _ in range(len(self.get_alias()), 10)
        )

        level_ = str(self.get_level()) + "".join(
            "_" for _ in range(len(str(self.get_level())), 3)
        )

        cold_ = str(self.get_cold()) + "".join(
            "_" for _ in range(len(str(self.get_cold())), 3)
        )

        hot_ = str(self.get_hot()) + "".join(
            "_" for _ in range(len(str(self.get_hot())), 3)
        )

        print("¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬")
        print(
            "| PLAYER: {} LEVEL: {} COLD: {} HOT: {} |".format(
                alias_, level_, cold_, hot_
            )
        )
        print("¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬")

    def reset_game(self):
        self.set_dead(False)
        self.set_level(0)
        self.set_hot(randint(-10, 10))
        self.set_cold(randint(-10, 10))

    def fight(self, player_2):
        """
        Fight with a oponent. Uses fight(player1, player2) function.
        """
        return fight(self, player_2)

    @DeprecationWarning
    def move(self, x, y):
        """
        Move to a adjacent position. Must be a range between -1 and 1.
        """
        position_move = (-2, -2)
        in_range = True

        # Correct range comprobation
        if x <= 1 and x >= -1:
            position_move[0] = x
        else:
            in_range = False

        if y <= 1 and y >= -1:
            position_move[1] = y
        else:
            in_range = False

        if in_range:
            # Set the position sum adjacent_move
            self.set_position(
                self.position[0] + position_move[0],
                self.position[1] + position_move[1],
                True,
            )
        else:
            raise OutOfRangeException(  # Case adjacent_move out of range raise an exception
                "Position move should be adjacent ranges from -1 to 1"
            )

    # SETTERS

    @DeprecationWarning
    def set_position(self, x=None, y=None, move=False):
        if x is not None:
            if x <= 19 and x >= 0 and y <= 19 and y >= 0:
                self.position = (x, y)
            else:
                raise OutOfRangeException

        if x is None and y is None:
            raise NoneValueException

    def set_alias(self, alias_input):
        if len(alias_input) > 20:
            raise OutOfRangeException("String length should be less to 20")

        if 0:
            raise IncorrectFormatException(
                "Incorrect format, string should be: [0..10 | a..z | A..Z]"
            )

        self.alias = alias_input

    def set_password(self, password):
        self.password = password

    def set_level(self, level_input):
        if level_input < 0:
            self.level = 0
        else:
            self.level = level_input

    def set_cold(self, cold_input):
        if cold_input >= -10 and cold_input <= 10:
            self.cold = cold_input
        else:
            raise OutOfRangeException("Cold should be between -10 and 10")

    def set_hot(self, hot_input):
        if hot_input >= -10 and hot_input <= 10:
            self.hot = hot_input
        else:
            raise OutOfRangeException("Hot should be between -10 and 10")

    def set_dead(self, dead):
        self.dead = dead

    # GETTERS

    @DeprecationWarning
    def get_position(self):
        return self.position

    def get_password(self):
        return hashlib.md5(self.password.encode()).hexdigest()

    def get_alias(self):
        return self.alias

    def get_level(self):
        return self.level

    def get_cold(self):
        return self.cold

    def get_hot(self):
        return self.hot

    def get_dead(self):
        return self.dead

    def get_dict(self):
        return {
            "alias": self.get_alias(),
            "password": self.get_password(),
            "level": self.get_level(),
            "cold": self.get_cold(),
            "hot": self.get_hot(),
            "dead": self.get_dead(),
        }
