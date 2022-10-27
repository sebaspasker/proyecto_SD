class NotPlayerException(Exception):
    "Exception when a position should be a player"

    def __init__(self, message="Position should be a player"):
        super().__init__(self, message)
