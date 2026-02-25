class LexError:
    def __init__(self, err_type, description, line, column, suggestion=None):
        self.type = err_type
        self.description = description
        self.line = line
        self.column = column
        self.suggestion = suggestion

    def to_dict(self):
        return {
            "type": self.type,
            "description": self.description,
            "line": self.line,
            "column": self.column,
            "suggestion": self.suggestion,
        }

    def __str__(self):
        s = f"{self.type}: {self.description} (Line {self.line}, Col {self.column})"
        if self.suggestion:
            s += f" — Suggestion: {self.suggestion}"
        return s

def make_invalid_char_suggestion(ch):
    # Suggest removing or replacing with similar safe characters
    if ch.isprintable():
        return f"Remove or replace '{ch}' with a valid identifier character (letters, digits, or '_'), or a valid operator/delimiter."
    return "Remove the invalid character"

def make_unterminated_string_suggestion(quote):
    return f"Add a closing {quote} at the end of the string, e.g. {quote}...{quote}."

def make_malformed_number_suggestion(lex):
    if lex.endswith('.'):
        return "Remove the trailing '.' or add digits after it, e.g. '5.0'"
    if lex.count('.') > 1:
        return "Remove extra decimal points; numeric literals should have at most one '.'"
    return "Check numeric format, e.g. 3.14"

def make_invalid_identifier_suggestion(lex):
    # propose a simple fix by prefixing underscore
    return f"Rename to '{'_' + lex}' or similar so it starts with a letter or underscore."

