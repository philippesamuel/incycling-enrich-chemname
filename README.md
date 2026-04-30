# find-cas

Resolve chemical compound names to CAS numbers via PubChem.

## Installation

### From GitHub

```bash
pip install git+https://github.com/philippesamuel/incycling-enrich-chemname.git
# or
uv pip install git+https://github.com/philippesamuel/incycling-enrich-chemname.git
```

### Clone and install

```bash
git clone https://github.com/philippesamuel/incycling-enrich-chemname.git
cd <repo>
pip install .
# or
uv pip install .
```

in editable mode

```bash
git clone https://github.com/philippesamuel/incycling-enrich-chemname.git
cd incycling-enrich-chemname
pip install -e .
# or
uv pip install -e .
```

## Usage

```bash
find-cas <input_dir> [--output-dir <output_dir>]
```

## Example

```bash
find-cas data/raw --output-dir data/output
```

Input CSVs must contain a 'Name' column. Output CSVs are written to data/output with an added 'CAS-Number' column.
