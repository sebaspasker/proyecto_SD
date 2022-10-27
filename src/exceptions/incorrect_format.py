class IncorrectFormatException(Exception):
    "Exception when input format is incorrect"

    def __init__(self, message="Input format is incorrect"):
        super().__init__(self, message)
