def process_position(position_):
    """
    Enters a position with format "[x.y]" and convert
    it as a tuple
    """
    postion_out = position[1:-2]
    x, y = position_out.split(".")
    return (x, y)
