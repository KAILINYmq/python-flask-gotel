import math

# millnames = ["", " Thousand", " Million", " Billion", " Trillion"]
millnames = ["", " K", " M", " B", " T"]


def number_to_text(n):
    """ convert large number to human readable text """
    n = float(n)
    millidx = max(
        0,
        min(
            len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))
        ),
    )

    return "{:.0f}{}".format(n / 10 ** (3 * millidx), millnames[millidx])
