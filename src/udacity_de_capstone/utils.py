"""
General utilities of the project.
Not my favorite kind of module to have, but oh well...
"""

from typing import Iterable, List


def format_column_names(cols: Iterable[str]) -> List[str]:
    """
    Utility for formatting column names.

    This trips them, makes them lowercase, and replaces spaces with underscores.
    """
    return list(map(lambda x: x.strip().lower().replace(" ", "_"), cols))
