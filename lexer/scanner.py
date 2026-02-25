import re
from .rules import KEYWORDS, OPERATORS, DELIMITERS, IDENT_RE, INT_RE, FLOAT_RE
from .errors import LexError

class Scanner:
    """
    Deterministic, character-by-character scanner with some regex checks.

    DFA approach (high-level):
    - Start in DEFAULT state.
    - When letter or '_' -> IDENTIFIER state: consume letters/digits/_ then classify as keyword/identifier.
    - When digit -> NUMBER state: consume digits, handle '.' for floats; validate malformed numbers.
    - When ' or " -> STRING state: consume until matching quote, handling escapes; report unterminated string.
    - When '/' followed by '/' or '*' -> COMMENT state: skip until end-of-line or closing */.
    - Operators and delimiters: try to match multi-char operators first then single char.
    - On any unexpected single character -> emit invalid-character error.
    """

    def __init__(self):
        # Build operator set for quick checks
        self._ops = sorted(OPERATORS, key=lambda x: -len(x))

    def scan(self, source, stop_on_error=False):
        tokens = []
        errors = []
        i = 0
        line = 1
        col = 1
        length = len(source)

        def current():
            return source[i] if i < length else ""

        while i < length:
            ch = source[i]
            # whitespace handling
            if ch == "\n":
                i += 1
                line += 1
                col = 1
                continue
            if ch.isspace():
                i += 1
                col += 1
                continue

            # comments
            if ch == "/":
                nxt = source[i+1] if i+1 < length else ""
                if nxt == "/":
                    # line comment
                    start_col = col
                    j = i+2
                    while j < length and source[j] != "\n":
                        j += 1
                    comment_text = source[i:j]
                    tokens.append({"type": "COMMENT", "value": comment_text, "line": line, "column": col})
                    col += (j - i)
                    i = j
                    continue
                elif nxt == "*":
                    # block comment
                    j = i+2
                    found = False
                    while j < length-1:
                        if source[j] == "*" and source[j+1] == "/":
                            found = True
                            j += 2
                            break
                        if source[j] == "\n":
                            line += 1
                            col = 1
                            j += 1
                        else:
                            j += 1
                            col += 1
                    if not found:
                        errors.append(LexError("Unterminated Comment", "Block comment not closed", line, col, suggestion="Close comment with '*/'"))
                        if stop_on_error:
                            return {"tokens": tokens, "errors": errors}
                    else:
                        tokens.append({"type": "COMMENT", "value": source[i:j], "line": line, "column": col})
                        col += (j - i)
                        i = j
                        continue

            # strings
            if ch == '"' or ch == "'":
                quote = ch
                start_col = col
                j = i+1
                value_chars = []
                escaped = False
                while j < length:
                    c = source[j]
                    if c == "\n":
                        # strings over multiple lines allowed? For this lexer, consider unterminated unless escaped newline
                        pass
                    if escaped:
                        value_chars.append(c)
                        escaped = False
                        j += 1
                        col += 1
                        continue
                    if c == "\\":
                        escaped = True
                        j += 1
                        col += 1
                        continue
                    if c == quote:
                        j += 1
                        col += 1
                        break
                    if c == "\n":
                        line += 1
                        col = 1
                    else:
                        col += 1
                    value_chars.append(c)
                    j += 1

                if j > length or (source[j-1] != quote):
                    # use suggestion helper
                    from .errors import make_unterminated_string_suggestion
                    suggestion = make_unterminated_string_suggestion(quote)
                    errors.append(LexError("Unterminated String", "String literal not terminated", line, start_col, suggestion=suggestion))
                    if stop_on_error:
                        return {"tokens": tokens, "errors": errors}
                    # recover by adding what we have
                    tokens.append({"type": "STRING", "value": ''.join(value_chars), "line": line, "column": start_col})
                    i = j
                    continue
                else:
                    tokens.append({"type": "STRING", "value": ''.join(value_chars), "line": line, "column": start_col})
                    i = j
                    continue

            # identifiers and keywords
            if ch.isalpha() or ch == "_":
                start = i
                start_col = col
                j = i+1
                while j < length and (source[j].isalnum() or source[j] == "_"):
                    j += 1
                lex = source[start:j]
                tok_type = "KEYWORD" if lex in KEYWORDS else "IDENTIFIER"
                tokens.append({"type": tok_type, "value": lex, "line": line, "column": start_col})
                col += (j - i)
                i = j
                continue

            # numbers
            if ch.isdigit():
                start = i
                start_col = col
                j = i
                has_dot = False
                while j < length and (source[j].isdigit() or (source[j] == '.' and not has_dot)):
                    if source[j] == '.':
                        has_dot = True
                    j += 1
                lex = source[start:j]
                # If after the numeric sequence there's an immediate letter or underscore,
                # then this looks like an identifier starting with a digit (invalid).
                next_char = source[j] if j < length else ''
                if next_char.isalpha() or next_char == '_':
                    # consume the rest of the alnum/underscore to present a single erroneous lexeme
                    k = j
                    while k < length and (source[k].isalnum() or source[k] == '_'):
                        k += 1
                    bad_lex = source[start:k]
                    from .errors import make_invalid_identifier_suggestion
                    suggestion = make_invalid_identifier_suggestion(bad_lex)
                    errors.append(LexError("Invalid Identifier", f"Identifier starts with digit '{bad_lex}'", line, start_col, suggestion=suggestion))
                    if stop_on_error:
                        return {"tokens": tokens, "errors": errors}
                    # try to recover by skipping the bad lexeme
                    i = k
                    col += (k - start)
                    continue

                # malformed if ends with '.' or has multiple dots
                if lex.count('.') > 1 or lex.endswith('.'):
                    from .errors import make_malformed_number_suggestion
                    suggestion = make_malformed_number_suggestion(lex)
                    errors.append(LexError("Malformed Number", f"Malformed numeric literal '{lex}'", line, start_col, suggestion=suggestion))
                    if stop_on_error:
                        return {"tokens": tokens, "errors": errors}
                else:
                    tok = "FLOAT" if '.' in lex else "INT"
                    tokens.append({"type": tok, "value": lex, "line": line, "column": start_col})
                col += (j - i)
                i = j
                continue

            # operators (try longest match)
            matched = False
            for op in self._ops:
                if source.startswith(op, i):
                    tokens.append({"type": "OPERATOR", "value": op, "line": line, "column": col})
                    i += len(op)
                    col += len(op)
                    matched = True
                    break
            if matched:
                continue

            # delimiters
            if ch in DELIMITERS:
                tokens.append({"type": "DELIMITER", "value": ch, "line": line, "column": col})
                i += 1
                col += 1
                continue

            # unexpected characters
            from .errors import make_invalid_char_suggestion
            suggestion = make_invalid_char_suggestion(ch)
            errors.append(LexError("Invalid Character", f"Unexpected character '{ch}'", line, col, suggestion=suggestion))
            if stop_on_error:
                return {"tokens": tokens, "errors": errors}
            i += 1
            col += 1

        return {"tokens": tokens, "errors": errors}
