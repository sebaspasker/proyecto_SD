def replace_string(string, replace):
    l_string = list(string)
    for i in range(len(list(replace))):
        l_string[i] = replace[i]
    return "".join(str(x) for x in l_string)


def replace_string_reverse(string, replace):
    l_string = list(string)
    for i in range(len(replace)):
        l_string[len(l_string) - len(replace) + i - 1] = replace[i]
    return "".join(str(x) for x in l_string)
