from enum import Enum, auto


class TokenType(Enum):
    OPEN_BRACE = auto()
    CLOSE_BRACE = auto()
    OPEN_PARENTHESIS = auto()
    CLOSE_PARENTHESIS = auto()
    SEMICOLON = auto()
    KEYWORD = auto()
    IDENTIFIER = auto()
    INTEGER_LITERAL = auto()
    MINUS = auto()
    BITWISE_NOT = auto()
    LOGICAL_NOT = auto()


keywords = [
    "u8",
    "return"
]


class Token:
    def __init__(self, token_type: TokenType, lexeme: str, line: int, value = None):
        self.token_type = token_type
        self.lexeme = lexeme
        self.line = line
        self.value = value

    def __repr__(self):
        return f"{self.token_type} '{self.lexeme}'"
