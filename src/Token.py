from enum import Enum
from typing import Any

class TokenType(Enum):
    # Special Tokens
    EOF = "EOF"
    ILLEGAL = "ILLEGAL"

    # Data Types
    INT = "INT"
    FLOAT = "FLOAT"
    IDENTIFIER = "IDENTIFIER"

    # Arithmetic Symbols
    PLUS = "PLUS"
    MINUS = "MINUS"
    ASTERISK = "ASTERISK"
    SLASH = "SLASH"
    POWER = "POWER"
    MODULUS = "MODULUS"

    # Assignment
    EQ = "EQ"

    # Symbols
    COLON = "COLON"
    NEWLINE = "NEWLINE"
    NEXTLINE = "NEXTLINE"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    ARROW = "ARROW"

    # Keywords
    RETURN = "RETURN"
    DEF = "DEF"
    PRINT = "PRINT"  # Add the PRINT token type for the print keyword

    # Typing
    TYPE = "TYPE"

    # String Type
    STRING = "STRING"


class Token:
    def __init__(self, type: TokenType, literal: Any, line_no: int, position: int) -> None:
        self.type = type
        self.literal = literal
        self.line_no = line_no
        self.position = position

    def __str__(self) -> str:
        return f"Token({self.type} : {self.literal}, Line : {self.line_no}, Position : {self.position})"

    def __repr__(self) -> str:
        return str(self)


# Keywords mapping
KEYWORDS: dict[str, TokenType] = {
    "def": TokenType.DEF,
    "return": TokenType.RETURN,
    "print": TokenType.PRINT  # Add the print keyword to the keywords mapping
}

# Type keywords
TYPE_KEYWORDS: list[str] = ["int", "float"]

def lookup_identifier(identifier: str) -> TokenType:
    """Looks up the identifier and returns the corresponding TokenType."""
    # Check for keywords
    tt: TokenType | None = KEYWORDS.get(identifier)
    if tt is not None:
        return tt

    # Check for type keywords
    if identifier in TYPE_KEYWORDS:
        return TokenType.TYPE

    # Check for string literals (assuming strings are enclosed in quotes)
    if identifier.startswith('"') and identifier.endswith('"'):
        return TokenType.STRING

    return TokenType.IDENTIFIER  # Default to IDENTIFIER for non-keywords