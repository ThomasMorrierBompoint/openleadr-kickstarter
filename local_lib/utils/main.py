import re
import unicodedata
from typing import List, Dict, Any


def extract_values_from_dicts(
    dictionaries: List[Dict[str, Any]],
    key_to_extract: str,
    default_value: Any = None,
    include_none: bool = False
) -> List[Any]:
    """
    Extract values corresponding to a specific key from a list of dictionaries.

    Args:
        dictionaries: List of dictionaries to extract values from
        key_to_extract: Key whose values should be extracted
        default_value: Value to use when key is missing (default: None)
        include_none: Whether to include None values in result (default: False)

    Returns:
        List of values associated with the specified key

    Example:
        >>> data = [{"id": 1}, {"id": 2}, {"id": None}]
        >>> extract_values_from_dicts(data, "id")
        [1, 2]
        >>> extract_values_from_dicts(data, "id", include_none=True)
        [1, 2, None]
    """
    values = [d.get(key_to_extract, default_value) for d in dictionaries]
    return values if include_none else [v for v in values if v is not None]


def slugify(s: str) -> str:
    """
    Sanitizes a given string by removing diacritics, replacing spaces with hyphens,
    and filtering out non-alphabetic characters and symbols except for hyphens.

    Parameters:
        s (str): The input string to sanitize.

    Returns:
        str: A sanitized string where diacritics are removed, spaces are replaced
        with hyphens, and only letters and hyphens remain.
    """
    # Normalize to remove diacritics
    s = unicodedata.normalize('NFKD', s)
    s = s.encode('ASCII', 'ignore').decode('utf-8')
    # Replace spaces with hyphens
    s = s.replace(' ', '-')
    # Remove all characters except letters and hyphens
    s = re.sub(r'[^a-zA-Z\-]', '', s)
    return s


def generate_id(prefix: str, index: int, timestamp: float) -> str:
    """
    Generates a unique identifier based on the given prefix, index, and timestamp.

    This function constructs an identifier string by combining a prefix, an index, and
    a timestamp. It is useful for creating unique identifiers for various entities.

    Arguments:
        prefix (str): A string prefix to include in the identifier. It provides context
            or categorization to the generated ID.
        index (int): An integer used as a unique identifier within its category or prefix.
        timestamp (float): A floating-point number representing a specific point in time.

    Returns:
        str: The generated unique identifier string.
    """
    return f'{prefix}-{index}'
    # return f'{prefix}{index}_{timestamp}'


# Copied from https://refactoring.guru/design-patterns/singleton/python/example
class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
