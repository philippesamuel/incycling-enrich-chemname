from typing import Any

import requests
from pydantic import BaseModel, Field

from app.main import PUBCHEM_API_URL, SYNONYMS_ENDPOINT_TEMPLATE

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

    def fetch_data(self, url: str) -> Json:
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
