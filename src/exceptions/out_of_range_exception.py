class OutOfRangeException(Exception):
    "Exception when a value is out of range"

    def __init__(self, message="Value out of range"):
        super().__init__(self, message)
