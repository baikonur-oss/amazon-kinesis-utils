from typing import List


def split_list(lst: list, n: int) -> List[list]:
    """
    Split a list of object in chunks of size n

    :param lst: List to split in chunks
    :param n: Size of chunk (last chunk may be less than n)
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
