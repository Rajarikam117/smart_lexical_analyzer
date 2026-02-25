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

VS Code
- Open the workspace folder (the one that contains `smart_lexer`).
- Select Python interpreter (Ctrl+Shift+P → `Python: Select Interpreter`).
- Use the provided launch configurations in `.vscode/launch.json`:
  - `Run Smart Lexer GUI` — launches the GUI
  - `Run Tests (unittest)` — runs the test suite

Output format

The tokenizer returns a dict with:

```json
{
  "tokens": [
    {"type": "IDENTIFIER", "value": "x", "line": 1, "column": 5},
    {"type": "INT", "value": "123", "line": 1, "column": 9}
  ],
  "errors": [ /* array of LexError objects (in-memory) */ ],
  "symbol_table": {"x": {"line":1, "column":5}}
}
```

Notes & tips
- Run the package with `python -m smart_lexer.main` to ensure imports resolve correctly.
- The GUI supports selecting an error and applying a heuristic quick-fix (e.g., append missing quote,
  remove a stray character, prefix an identifier with `_`). Use the File → Save in the editor after fixes.
- If you see import errors, ensure your current working directory is the workspace root (the folder
  that contains `smart_lexer`) or run with the `-m` module form.

Want more?
- I can add: richer quick-fixes with preview/undo, CSV export for tokens, or make the tokens table sortable.
  Tell me which one you'd like next.
