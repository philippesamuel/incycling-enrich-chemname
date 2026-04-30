from enum import StrEnum
from pathlib import Path
from typing import Iterable, Optional

from charset_normalizer import CharsetMatch
import polars as pl
import typer
from loguru import logger
from requests import Session
from requests.exceptions import RequestException
from requests_cache import CacheMixin
from requests_ratelimiter import LimiterMixin

from app.client import PubChemClient
from app.config import CACHE_EXPIRE_AFTER, CAS_PATTERN, RATE_LIMIT_PER_SECOND


app = typer.Typer()


class ErrorFlags(StrEnum):
    ERROR = "ERROR"
    NOT_FOUND = "NOT_FOUND"


@app.command()
def main(
    input_dir: Path,
    output_dir: Optional[Path] = None,
) -> None:
    if output_dir is None:
        output_dir = input_dir.parent / "output"

    if not input_dir.exists():
        raise ValueError("Input directory does not exist. Pass a valid folder")
    if not input_dir.is_dir():
        raise ValueError("Input must be a valid folder")

    # create output folder, do not raise exception if it already exists
    output_dir.mkdir(exist_ok=True)

    with build_session() as s:
        client = PubChemClient(session=s)
        files = get_files(input_dir)
        for file in files:
            out_file = output_dir / file.name
            names = get_compound_names(file)
            cas_numbers: list[str] = []
            for name in names:
                try:
                    logger.info(f"Fetching info for {name}")
                    compound_info = client.get_compound_info(name.lower())
                except (RequestException, ValueError) as e:
                    logger.error(f"Error fetching info: {e}")
                    cas_numbers.append(ErrorFlags.ERROR)
                else:
                    cas_number = find_first_cas_number(compound_info.synonym)
                    if cas_number is None:
                        cas_numbers.append(ErrorFlags.NOT_FOUND)
                    else:
                        cas_numbers.append(cas_number)

            df = pl.DataFrame({"Name": names, "CAS-Number": cas_numbers})
            df.write_csv(out_file)


class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass


def build_session() -> Session:
    return CachedLimiterSession(
        per_second=RATE_LIMIT_PER_SECOND, 
        expire_after=CACHE_EXPIRE_AFTER,
    )


def get_files(folder: Path) -> Iterable[Path]:
    yield from folder.glob("*.csv")


def get_compound_names(file: Path) -> list[str]:
    names = pl.read_csv(file, columns=["Name"]).to_series()
    return names.to_list()


def find_first_cas_number(strings: list[str]) -> str | None:
    for s in strings:
        if m := CAS_PATTERN.search(s):
            number = m.group("number")
            cas_number = f"CAS-{number}"
            logger.success(f"Found CAS number: {cas_number}")
            return cas_number
    logger.warning("No CAS number found")
    return None


if __name__ == "__main__":
    app()
