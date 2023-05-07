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


def rich_error_wrapper(msg: str) -> str:
    """Wraps a string for errors with rich formatting for nicer logging.

    Example:
        err = "my error message" \n
        log.error(rich_error_wrapper(err), extra={"markup": True})
    """
    return f"[bold red]{msg}[/]"


def rich_success_wrapper(msg: str) -> str:
    """Wraps a string for success with rich formatting for nicer logging.

    Example:
        err = "checks passed" \n
        log.info(rich_success_wrapper(err), extra={"markup": True})
    """
    return f"[green]{msg}[/]"
