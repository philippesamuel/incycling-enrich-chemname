from datetime import timedelta
from pathlib import Path
import re
from typing import Any, Iterable, Optional

import requests
from requests.exceptions import RequestException
from requests_cache import CachedSession
from ratelimit import limits, sleep_and_retry
from pydantic import BaseModel, Field
import polars as pl
import typer

from loguru import logger

from icecream import ic

PUBCHEM_API_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
SYNONYMS_ENDPOINT_TEMPLATE = "compound/name/{compound_name}/synonyms/JSON"

# regex for CAS pattern (e.g., 'CAS-50-00-0')
CAS_PATTERN = re.compile(r"^(CAS-)?(?P<number>\d{2,7}-\d{2}-\d$)")


type Json = dict[str, Any]


class CompoundInfo(BaseModel):
    cid: int = Field(
        ..., alias="CID", validation_alias="CID", description="Compound ID"
    )
    synonym: list[str] = Field(
        default_factory=list,
        description="List of synonyms for a the compound",
        alias="Synonym",
        validation_alias="Synonym",
    )


class PubChemClient:
    """PubChem client to fetch compound information."""
    def __init__(self, session: requests.Session) -> None:
        self.session = session
    
    def get_compound_info(self, compound_name: str) -> CompoundInfo:
        endpoint = SYNONYMS_ENDPOINT_TEMPLATE.format(compound_name=compound_name)
        url = f"{PUBCHEM_API_URL}{endpoint}"
        data = self.fetch_data(url)

        if e := data.get("Fault"):
            raise ValueError(f"Error: {e}")
        try:
            info = data["InformationList"]["Information"][0]
        except KeyError as e:
            raise ValueError(f"Unexpected JSON schema in {data}")
        return CompoundInfo(**info)
    
    @sleep_and_retry
    @limits(calls=5, period=1)
    def fetch_data(self, url: str) -> Json:
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
        
    

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
    
    with CachedSession(expire_after=timedelta(hours=1)) as s:
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
            
            ic(df)
            df.write_csv(out_file)


def get_files(folder: Path) -> Iterable[Path]:
    yield from folder.glob('*.csv')


def get_compound_names(file: Path) -> list[str]:
    names = (
        pl.read_csv(file, columns=["Name"])
        .to_series()
        )
    return names.to_list()


def find_first_cas_number(strings: list[str]) -> str | None:
    for s in strings:
        if m := CAS_PATTERN.match(s):
            number = m.group('number')
            cas_number = f"CAS-{number}"
            logger.success(f"Found CAS number: {cas_number}")
            return cas_number
    logger.warning("No CAS number found")
    return None


if __name__ == "__main__":
    app()
