from src.errors import LexicalError


class Token:
    def __init__(self, kind, value, position):
        self.kind = kind
        self.value = value
        self.position = position

    def __repr__(self):
        return f"Token({self.kind}, {self.value!r}, {self.position})"

SINGLE_CHAR_TOKENS = {
    "(": "LPAREN",
    ")": "RPAREN",
    "[": "LBRACKET",
    "]": "RBRACKET",
    "{": "LBRACE",
    "}": "RBRACE",
    ",": "COMMA",
    ".": "DOT",
}


def tokenize(source):
    tokens = []
    i = 0

    while i < len(source):
        char = source[i]

        # Ignore whitespace
        if char.isspace():
            i += 1
            continue

        # Ignore // comments
        if char == "/" and i + 1 < len(source) and source[i + 1] == "/":
            i += 2
            while i < len(source) and source[i] != "\n":
                i += 1
            continue

        # Punctuation
        if char in SINGLE_CHAR_TOKENS:
            tokens.append(Token(SINGLE_CHAR_TOKENS[char], char, i))
            i += 1
            continue

        # Quoted string
        if char == "'":
            token, i = scan_string(source, i)
            tokens.append(token)
            continue

        # Number, including negative numbers
        if char.isdigit() or (
            char == "-"
            and i + 1 < len(source)
            and source[i + 1].isdigit()
        ):
            token, i = scan_number(source, i)
            tokens.append(token)
            continue

        # Identifier
        if char.isalpha() or char == "_":
            start = i
            i += 1

            while i < len(source):
                if source[i].isalnum() or source[i] == "_":
                    i += 1
                else:
                    break

            tokens.append(Token("IDENT", source[start:i], start))
            continue

        # Comparison operators
        if char in "=!<>":
            token, i = scan_operator(source, i)
            tokens.append(token)
            continue

        raise LexicalError(f"unexpected character {char!r}", i)

    tokens.append(Token("EOF", None, len(source)))
    return tokens


def scan_operator(source, i):
    start = i
    char = source[i]

    # Maximal munch: check for a two-character operator first.
    if i + 1 < len(source) and source[i + 1] == "=":
        pair = source[i:i + 2]

        kinds = {
            "!=": "NE",
            "<=": "LE",
            ">=": "GE",
        }

        if pair in kinds:
            return Token(kinds[pair], pair, start), i + 2

    kinds = {
        "=": "EQ",
        "<": "LT",
        ">": "GT",
    }

    if char in kinds:
        return Token(kinds[char], char, start), i + 1

    raise LexicalError(f"invalid operator starting with {char!r}", start)


def scan_number(source, i):
    start = i

    if source[i] == "-":
        i += 1

    while i < len(source) and source[i].isdigit():
        i += 1

    if (
        i < len(source)
        and source[i] == "."
        and i + 1 < len(source)
        and source[i + 1].isdigit()
    ):
        i += 1

        while i < len(source) and source[i].isdigit():
            i += 1

    text = source[start:i]

    if "." in text:
        value = float(text)
    else:
        value = int(text)

    return Token("NUMBER", value, start), i


def scan_string(source, i):
    start = i
    i += 1
    characters = []

    while i < len(source):
        if source[i] == "'":

            # Two single quotes mean one literal quote.
            if i + 1 < len(source) and source[i + 1] == "'":
                characters.append("'")
                i += 2
                continue

            i += 1
            return Token("STRING", "".join(characters), start), i

        characters.append(source[i])
        i += 1

    raise LexicalError("unterminated string", start)