from pathlib import Path
from typing import Optional, Protocol

import typer
from loguru import logger
from typer import Argument, Option

from app.client import PubChemClient
from app.data_io import get_compound_names, get_files, handle_io_dir, write_csv_file
from app.session import build_session
from app.types import ColEnum

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
)


class CASResolver(Protocol):
    def resolve_cas(self, name: str) -> str: ...


@app.command(no_args_is_help=True)
def main(
    input_dir: Path = Argument(
        ...,
        help=f"Folder containing input CSV files with a '{ColEnum.NAME}' column.",
    ),
    output_dir: Optional[Path] = Option(
        None,
        "-o",
        "--output-dir",
        help="Folder to write enriched CSV files. Defaults to '<input_dir>/../output'.",
    ),
) -> None:
    """Resolve compound names to CAS numbers via PubChem for all CSV files in INPUT_DIR."""
    input_dir, output_dir = handle_io_dir(input_dir, output_dir)

    with build_session() as s:
        client = PubChemClient(session=s)
        files = get_files(input_dir)
        for file in files:
            out_file = output_dir / file.name
            if out_file.exists():
                logger.warning("Overwriting existing file {}", out_file)
            process_file(client, file=file, out_file=out_file)


def process_file(client: CASResolver, file: Path, out_file: Path) -> None:
    names = get_compound_names(file)
    cas_numbers = [client.resolve_cas(name) for name in names]
    write_csv_file(
        out_file,
        data={
            ColEnum.NAME: names,
            ColEnum.CAS: cas_numbers,
        },
    )


if __name__ == "__main__":
    app()
