from pathlib import Path
from typing import Iterable

import polars as pl


def get_files(folder: Path) -> Iterable[Path]:
    yield from folder.glob("*.csv")


def get_compound_names(file: Path) -> list[str]:
    names = pl.read_csv(file, columns=["Name"]).to_series()
    return names.to_list()