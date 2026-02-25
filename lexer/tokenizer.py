from .scanner import Scanner
from .errors import LexError
from .symbol_table import SymbolTable

class Tokenizer:
    def __init__(self):
        self.scanner = Scanner()

    def analyze(self, source, mode="AI"):
        """
        mode: 'Manual' or 'AI'.
        Manual: stop at first lexical error.
        AI: collect all errors.
        Returns dict { tokens: [...], errors: [...] }
        """
        stop_on_error = True if mode.lower().startswith('manual') else False
        res = self.scanner.scan(source, stop_on_error=stop_on_error)
        tokens = res.get('tokens', [])
        errors = res.get('errors', [])

        # Build symbol table and check for duplicate declarations.
        symtab = SymbolTable()
        # Simple pass: treat identifiers that follow declaration keywords as declarations
        decl_keywords = {'var', 'let', 'const', 'function'}
        prev = None
        for tok in tokens:
            if tok['type'] == 'IDENTIFIER':
                if prev and prev.get('type') == 'KEYWORD' and prev.get('value') in decl_keywords:
                    name = tok['value']
                    existing = symtab.add(name, tok['line'], tok['column'])
                    if existing:
                        suggestion = f"Rename or remove duplicate '{name}' (first declared at line {existing['line']}, col {existing['column']})"
                        errors.append(LexError('Duplicate Declaration', f"Identifier '{name}' already declared", tok['line'], tok['column'], suggestion=suggestion))
            prev = tok

        # Return structured output
        return {
            'tokens': tokens,
            'errors': errors,
            'symbol_table': symtab.all()
        }
