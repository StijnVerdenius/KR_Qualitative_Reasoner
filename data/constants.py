MIN, NEG, NULL, POS, MAX = -2, -1, 0, 1, 2

CONSTANTS_DICT = {"MIN": MIN, "NEG": NEG, "NULL" : NULL, "POS" : POS, "MAX": MAX}

def readout_constants(constant_list):
    return tuple([CONSTANTS_DICT[elem] for elem in constant_list])