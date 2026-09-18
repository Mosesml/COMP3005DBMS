class LexicalError(Exception):
    def __init__(self, message, position):
        self.message = message
        self.position = position
        super().__init__(f"Lexical error at position {position}: {message}")


class ParseError(Exception):
    def __init__(self, message, position):
        self.message = message
        self.position = position
        super().__init__(f"Syntax error at position {position}: {message}")
