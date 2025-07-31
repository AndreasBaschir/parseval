# comsol_spice_parser_evaluator

## Overview

`comsol_spice_parser_evaluator` is a Python library and toolset for parsing, evaluating, and converting mathematical expressions between COMSOL and SPICE formats. It provides an `ExprParser` class for handling these tasks.

## Current Features

- Parse SPICE and COMSOL mathematical expressions into ASTs
- Generate expressions in both SPICE and COMSOL formats
- Evaluate expressions numerically with variable substitution
- Includes test cases and example scripts
- Modular design for easy extension and integration
- Parametrized tests to be used with `pytest`

## Features to be Implemented

- Add `logging` and error handling
- Add `argparse` for command line usage

## Project Structure

```
comsol_spice_parser_evaluator/
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   └── ... (test cases, CSVs)
├── scripts/
│   └── parser_testcases.py
├── src/
│   ├── __init__.py
│   ├── expr_parser.py
│   ├── evaluators/
│   │   ├── __init__.py
│   │   └── pyxeval.py
│   └── parsers/
│       ├── __init__.py
│       ├── spice_parser.py
│       └── comsol_parser.py
└── tests/
    └── test_expr_parser.py
```

## Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd comsol_spice_parser_evaluator
   ```
2. (Optional) Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

`expr_parser.py` is the main entry point for parsing and evaluating expressions. It has 6 main methods besides the constructor:

```python
class ExprParser:
   def __init__(self, expr: str, varnames: list, initial_lang: str = None):
      ...
   def aeval(self, *args):
      ...
   def keval(self, **kwargs):
      ...
   def parse_spice(self):
      ...
   def parse_comsol(self):
      ...
   def generate_spice(self):
      ...
   def generate_comsol(self):
   ...
```

### As a Library

```python
from src.expr_parser import ExprParser

# Parse a SPICE expression
parser = ExprParser("(-0.0036*(temp+273.15)**2+4.6305*(temp+273.15)-405.38)*3210", ["temp"], language="spice")
result = parser.aeval(25)  # Evaluate with temp=25
```

### From the Command Line

You can run the following example scripts:

```bash
python3 -m src.expr_parser
python3 src/parsers/spice_parser.py
python3 src/parsers/comsol_parser.py
```

## Testing

This project uses [pytest](https://docs.pytest.org/) for testing. To run all tests, simply execute:

```bash
pytest
```

The main test suite is in `tests/test_expr_parser.py` and covers two types of tests:

1. **Evaluation Tests**: These tests check that the `ExprParser` evaluates SPICE and COMSOL expressions correctly and consistently, using both positional (`aeval`) and keyword (`keval`) argument evaluation. They also compare results between SPICE and COMSOL forms for equivalence.

2. **Generation Tests**: These tests verify that the `ExprParser` can generate correct SPICE and COMSOL expressions from the AST, ensuring round-trip conversion between formats is accurate.

Both test types are parametrized using data from `data/spice_comsol_values.csv`.

## Development

- Source code is in the `src/` directory.
- Add new parsers or evaluators in their respective subfolders.
- Test cases and data are in `data/` and `tests/`.
- Add imports to `__init__.py` files as needed to expose functionality.

## Contributing

Pull requests and issues are welcome! Please:
- Follow PEP8 style guidelines
- Add tests for new features
- Document your code
