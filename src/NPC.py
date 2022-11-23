from .exceptions.out_of_range_exception import OutOfRangeException
from random import randint


class NPC:
    position = (0, 0)
    alias = ""
    level = 0
    dead = False

    def __init__(self, list_str=None):
        if list_str is not None:
            self.position = (int(list_str[0]), int(list_str[1]))
            self.alias = list_str[0]
            self.level = int(list_str[1])

    def __str__(self):
        return "NPC: {}, level: {}".format(self.alias, self.level)

    def create_random(self, id_):
        self.set_alias("NPC_{}".format(id_))
        self.set_level(randint(0, 9))
        self.set_position(randint(0, 19), randint(0, 19))

    # SETTERS

    def set_level(self, level):
        if level >= 0 and level < 10:
            self.level = level
        else:
            raise OutOfRangeException("El nivel del NPC tiene que estar entre 0 y 9")

    def set_alias(self, alias):
        self.alias = alias

    def set_position(self, x, y):
        if x >= 0 and x <= 19 and y >= 0 and y <= 19:
            self.position(x, y)
        else:
            raise OutOfRangeException(
                "La posición del NPC tiene que estar entre 0 y 19. (̣{},{})".format(
                    x, y
                )
            )

    # GETTERS

    def get_alias(self):
        return self.alias

    def get_level(self):
        return self.level
