colors = [
    "red",
    "green",
    "blue",
    "orange",
    "yellow",
    "pink",
    "grey",
    "brown",
    "olive",
    "cyan",
    "purple",
    "darksalmon",
    "lime",
    "dodgerblue",
    "springgreen",
    "hotpink",
]


def get_complementair(color: str)->str:
    if color == "red":
        return "cyan"
    if color == "green":
        return "pink"
    if color == "blue":
        return "yellow"
    if color == "orange":
        return "purple"
    if color == "yellow":
        return "blue"
    if color == "pink":
        return "green"
    if color == "grey":
        return "lime"
    if color == "brown":
        return "hotpink"
    if color == "olive":
        return "dodgerblue"

    return "black"
