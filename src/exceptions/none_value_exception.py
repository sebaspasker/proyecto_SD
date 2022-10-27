class NoneValueException(Exception):
    "Exception when a input value is None"

    def __init__(self, message="Input value can't be None"):
        super().__init__(self, message)
