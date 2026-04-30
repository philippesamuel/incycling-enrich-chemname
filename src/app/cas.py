import re

# regex for CAS pattern (e.g., 'CAS-50-00-0')
CAS_PATTERN = re.compile(r"(CAS-)?(?P<number>\d{2,7}-\d{2}-\d)")


def find_first_cas_number(strings: list[str]) -> str | None:
    for s in strings:
        if m := CAS_PATTERN.search(s):
            return m.group("number")
    return None
