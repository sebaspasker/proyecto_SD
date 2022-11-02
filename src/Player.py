# TODO Search correct exception route
from .exceptions.none_value_exception import NoneValueException
from .exceptions.incorrect_format import IncorrectFormatException
from .exceptions.out_of_range_exception import OutOfRangeException
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
    def __init__(self):
        self.position = (1, 1)
        self.alias = ""
        self.level = 0
        self.cold = 0
        self.hot = 0
        self.dead = False

    def fight(self, player_2):
        """
        Fight with a oponent. Uses fight(player1, player2) function.
        """
        return fight(self, player_2)

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

    def set_position(self, x=None, y=None, move=False):
        if x is not None:
            if x <= 20 and x >= 1:
                self.position[0] = x
            else:
                raise OutOfRangeException

        if y is not None:
            if x <= 20 and x >= 1:
                self.position[1] = y
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

    def set_level(self, level_input):
        if level_input <= 0:
            raise OutOfRangeException("Level should be higher or equal to 0")

        self.level = level_input

    def set_cold(self, cold_input):
        if cold_input >= -10 and cold_input <= 10:
            self.colf = cold_input
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

    def get_position(self):
        return self.position

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
