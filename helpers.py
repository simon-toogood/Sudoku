def average_colours(c1, c2):
    """Takes the geometric average of two hex colours."""
    def hextorgb(h):
        return tuple(int(h[i:i + 2], 16) / 255. for i in (1, 3, 5))
    def rgbtohex(rgb):
        return f'#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}'
    rgb = (hextorgb(c1), hextorgb(c2))
    return rgbtohex([sum(y) / len(y) for y in zip(*rgb)])


def check_duplicates(lst):
    """Check for duplicate values in a list of Cells or integers. Returns a list of duplicates values as integers,
    or an empty list if there are none"""
    lst.sort()
    out = []
    prev = None
    for item in lst:
        if item == prev:
            if item not in out:
                out.append(item)
        else:
            prev = item
    return [a.number for a in out]