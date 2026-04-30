from pathlib import Path
from typing import Iterable, Optional, Sequence

import polars as pl

from app.types import ColEnum

COLUMNS = [ColEnum.NAME]


def handle_io_dir(input_dir: Path, output_dir: Optional[Path]) -> tuple[Path, Path]:
    input_dir, output_dir = validate_io_dir(input_dir, output_dir)
    # create output folder, do not raise exception if it already exists
    output_dir.mkdir(exist_ok=True)
    return input_dir, output_dir


def validate_io_dir(input_dir: Path, output_dir: Optional[Path]) -> tuple[Path, Path]:
    if output_dir is None:
        output_dir = input_dir.parent / "output"
    if input_dir.resolve() == output_dir.resolve():
        raise ValueError("Output folder cannot be the same as input folder.")
    if not input_dir.exists():
        raise ValueError("Input folder does not exist. Pass a valid folder.")
    if not input_dir.is_dir():
        raise ValueError("Input must be a valid folder.")
    return input_dir, output_dir


def get_files(folder: Path) -> Iterable[Path]:
    yield from folder.glob("*.csv")


def get_compound_names(file: Path) -> list[str]:
    names = pl.read_csv(file, columns=COLUMNS).to_series()
    return names.to_list()


def write_csv_file(out_file: str | Path, data: dict[str, Sequence]) -> None:
    pl.DataFrame(data).write_csv(out_file)
