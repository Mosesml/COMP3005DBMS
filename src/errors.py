class LexicalError(Exception):
    def __init__(self, message, position):
        self.message = message
        self.position = position
        super().__init__(f"Lexical error at position {position}: {message}")