def process_position(position_):
    """
    Enters a position with format "[x.y]" and convert
    it as a tuple
    """
    position_out = position_[1:-1]
    x, y = position_out.split(".")
    return (int(x), int(y))


def position_str(position):
    return "[{}.{}]".format(str(position[0]), str(position[1]))
