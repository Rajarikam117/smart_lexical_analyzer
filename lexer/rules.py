import re

# Keywords, operators, delimiters
KEYWORDS = {
    "if",
    "else",
    "for",
    "while",
    "return",
    "function",
    "var",
    "let",
    "const",
    "true",
    "false",
    "null",
}

OPERATORS = [
    "==", "!=", "<=", ">=", "=", "+", "-", "*", "/", "%", "<", ">", "&&", "||", "!",
]

DELIMITERS = {
    "(", ")", "{", "}", "[", "]", ",", ";", ":",
}

# regex patterns
IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
INT_RE = re.compile(r"^[0-9]+$")
FLOAT_RE = re.compile(r"^[0-9]+\.[0-9]+$")
