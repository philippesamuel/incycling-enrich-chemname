import re
from datetime import timedelta
from pathlib import Path
from typing import Iterable, Optional

import polars as pl
import typer
from loguru import logger
from requests import Session
from requests.exceptions import RequestException
from requests_cache import CachedSession
from requests_ratelimiter import LimiterSession

from app.client import PubChemClient

PUBCHEM_API_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
SYNONYMS_ENDPOINT_TEMPLATE = "compound/name/{compound_name}/synonyms/JSON"

# regex for CAS pattern (e.g., 'CAS-50-00-0')
CAS_PATTERN = re.compile(r"^(CAS-)?(?P<number>\d{2,7}-\d{2}-\d$)")


app = typer.Typer()


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

    with session_factory() as s:
        client = PubChemClient(session=s)
        files = get_files(input_dir)
        for file in files:
            out_file = output_dir / file.name
            names = get_compound_names(file)
            cas_numbers = []
            for name in names:
                try:
                    logger.info(f"Fetching info for {name}")
                    compound_info = client.get_compound_info(name.lower())
                except (RequestException, ValueError) as e:
                    logger.error(f"Error fetching info: {e}")
                    cas_numbers.append("ERROR")
                else:
                    cas_number = find_first_cas_number(compound_info.synonym)
                    cas_numbers.append(cas_number)

            df = pl.DataFrame([names, cas_numbers], schema=["Name", "CAS-Number"])
            df.write_csv(out_file)


def session_factory() -> Session:
    cached_session = CachedSession(expire_after=timedelta(hours=1))
    return LimiterSession(per_second=4, session=cached_session)


def get_files(folder: Path) -> Iterable[Path]:
    yield from folder.glob("*.csv")


def get_compound_names(file: Path) -> list[str]:
    names = pl.read_csv(file, columns=["Name"]).to_series()
    return names.to_list()


def find_first_cas_number(strings: list[str]) -> str | None:
    for s in strings:
        if m := CAS_PATTERN.match(s):
            number = m.group("number")
            cas_number = f"CAS-{number}"
            logger.success(f"Found CAS number: {cas_number}")
            return cas_number
    logger.warning("No CAS number found")
    return None


if __name__ == "__main__":
    app()
