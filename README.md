# Smart Lexical Analyzer

Lightweight, modular lexical analyzer with a tkinter GUI and intelligent error reporting.

Contents
- `smart_lexer/` — main package
  - `main.py` — GUI entry point
  - `gui/app.py` — tkinter GUI (editor, tokens table, error list, suggestions)
  - `lexer/` — tokenizer and scanner implementation
  - `utils/helpers.py` — small JSON helpers
  - `tests/` — unit tests and headless runner

Key features
- Deterministic DFA-like scanner (char-by-char) plus regex checks
- Recognizes keywords, identifiers, ints/floats, strings, operators, delimiters, comments
- Symbol table with duplicate-declaration detection
- Error classification: invalid characters, unterminated strings/comments, malformed numbers,
  identifiers that start with digits, unexpected symbol sequences
- Two modes: `Manual Mode` (stop at first error) and `AI Mode` (collect all errors)
- GUI shows tokens in a table and errors in a selectable list with suggested quick-fixes

Quick start (Windows / PowerShell)

1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. (No external dependencies) Run the GUI:

```powershell
python -m smart_lexer.main
```

3. Headless example (prints JSON):

```powershell
python -m smart_lexer.tests.run_test
```

4. Run unit tests:

```powershell
python -m unittest discover -v smart_lexer/tests
```

Installation & packaging
------------------------

You can run the project from source (recommended during development) or install it as a package.

Install from source into a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install .
```

After installing the package, the console script `smart-lexer` is available:

```powershell
smart-lexer    # launches the GUI (same as `python -m smart_lexer.main`)
```

Build a wheel and source distribution for publishing (see `PUBLISHING.md`):

```powershell
python -m pip install --upgrade build twine
python -m build
```

Publish to Test PyPI or PyPI with `twine` (see `PUBLISHING.md`).


VS Code
- Open the workspace folder (the one that contains `smart_lexer`).
- Select Python interpreter (Ctrl+Shift+P → `Python: Select Interpreter`).
- Use the provided launch configurations in `.vscode/launch.json`:
  - `Run Smart Lexer GUI` — launches the GUI
  - `Run Tests (unittest)` — runs the test suite

Output format

There are two common ways to view tokens:

- Headless / programmatic JSON (used by the test runner and APIs):

```json
{
  "tokens": [
    {"type": "IDENTIFIER", "value": "x", "line": 1, "column": 5},
    {"type": "INT", "value": "123", "line": 1, "column": 9}
  ],
  "errors": [],
  "symbol_table": {"x": {"line":1, "column":5}}
}
```

- GUI table (what you see in the `Tokens` panel of the tkinter app):

The GUI presents tokens in a sortable table with the following columns:

| Type | Value | Line | Column |
|------|-------:|-----:|-------:|
| IDENTIFIER | x | 1 | 5 |
| INT | 123 | 1 | 9 |

Use the table headers to sort tokens by any column. The GUI also allows copying or exporting the table contents via future enhancements.

Notes & tips
- Run the package with `python -m smart_lexer.main` to ensure imports resolve correctly.
- The GUI supports selecting an error and applying a heuristic quick-fix (e.g., append missing quote,
  remove a stray character, prefix an identifier with `_`). Use the File → Save in the editor after fixes.
- If you see import errors, ensure your current working directory is the workspace root (the folder
  that contains `smart_lexer`) or run with the `-m` module form.

Want more?
- I can add: richer quick-fixes with preview/undo, CSV export for tokens, or make the tokens table sortable.
  Tell me which one you'd like next.
