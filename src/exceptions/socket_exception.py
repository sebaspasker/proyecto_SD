class SocketException(Exception):
    "Exception when the socket message is not correct"

    def __init__(self, message="Socket message error"):
        super().__init__(self, message)
