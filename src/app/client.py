from typing import Any

import requests
from loguru import logger
from pydantic import BaseModel, Field
from requests.exceptions import RequestException

from app.cas import find_first_cas_number
from app.config import PUBCHEM_API_URL, SYNONYMS_ENDPOINT_TEMPLATE
from app.main import ErrorFlags

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

    def __init__(self, session: requests.Session):
        self.session = session

    def resolve_cas(self, name: str) -> str:
        try:
            logger.info(f"Fetching info for {name}")
            info = self.get_compound_info(name.lower())
        except (RequestException, ValueError) as e:
            logger.error(f"Error fetching info: {e}")
            return ErrorFlags.ERROR
        else:
            cas_number = find_first_cas_number(info.synonym)
            if cas_number is not None:
                return cas_number
            return ErrorFlags.NOT_FOUND

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

    def fetch_data(self, url: str) -> Json:
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
