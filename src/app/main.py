from pathlib import Path
from typing import Optional, Protocol

import typer
from loguru import logger

from app.client import PubChemClient
from app.data_io import get_compound_names, get_files, handle_io_dir, write_csv_file
from app.session import build_session
from app.types import ColEnum

app = typer.Typer()


class CASResolver(Protocol):
    def resolve_cas(self, name: str) -> str: ...


@app.command()
def main(
    input_dir: Path,
    output_dir: Optional[Path] = None,
) -> None:
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
