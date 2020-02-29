import logging
from typing import List, Any

logger = logging.getLogger("kinesis_logging_utils")
logger.setLevel(logging.INFO)


def split_list(lst: list, n: int) -> List[list]:
    """
    Split a list of object in chunks of size n

    :param lst: List to split in chunks
    :param n: Size of chunk (last chunk may be less than n)
    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def dict_get_default(
    dictionary: dict, key: str, default: any, verbose: bool = False
) -> Any:
    """
    Get key from dictionary if key is in dictionary, default value otherwise

    :param dictionary: dictionary to retrieve key from
    :param key: key name in dictionary
    :param default: value to return if key is not in dictionary
    :param verbose: output detailed warning message when returning default value
    :return: value for key if key is in dictionary, default value otherwise
    """
    if key not in dictionary:
        if verbose:
            logger.warning(
                f'Cannot retrieve field "{key}" from data: {dictionary}, '
                f"falling back to default value: {default}"
            )
        return default, True

    else:
        return dictionary[key], False
