import re

from loguru import logger

# regex for CAS pattern (e.g., 'CAS-50-00-0')
CAS_PATTERN = re.compile(r"(CAS-)?(?P<number>\d{2,7}-\d{2}-\d)")


def find_first_cas_number(strings: list[str]) -> str | None:
    for s in strings:
        if m := CAS_PATTERN.search(s):
            number = m.group("number")
            cas_number = f"CAS-{number}"
            logger.success(f"Found CAS number: {cas_number}")
            return cas_number
    logger.warning("No CAS number found")
    return None
