# TODO Search correct exception route
from exceptions import NoneValueException


def fight(player_1, player_2):
    # TODO
    pass


class Player:
    def __init__(self):
        self.position = (1, 1)
        self.alias = ""
        self.level = 0
        self.cold = 0
        self.hot = 0

    def set_position(self, x=None, y=None):
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
        # TODO
        pass

    def set_hot(self, hot_input):
        # TODO
        pass
