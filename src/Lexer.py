from typing import Any

from Token import Token
from Token import TokenType
from Token import lookup_identifier


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source

        self.position: int = 0
        self.read_position: int = 0
        self.line_no: int = 1

        self.current_char: str | None = None

        self.__read_char()

    def __read_char(self) -> None:
        if self.read_position >= len(self.source):
            self.current_char = None
        else:
            self.current_char = self.source[self.read_position]

        self.position = self.read_position
        self.read_position += 1

    def __peek_char(self) -> str | None:
        """Peeks to the upcoming char without advancing the lexer"""
        if self.read_position >= len(self.source):
            return None

        return self.source[self.read_position]

    def __skip_whitespace(self) -> None:
        while self.current_char in [' ', '\t', '\r']:
            if self.current_char == '\n':
                self.line_no += 1

            self.__read_char()

    def __new_token(self, tt: TokenType, literal: Any) -> Token:
        return Token(type = tt, literal = literal, line_no = self.line_no, position = self.position)

    def __is_digit(self, ch: str) -> bool:
        return '0' <= ch <= '9'

    def __is_letter(self, ch: str) -> bool:
        return 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or ch == '_'

    def __read_number(self) -> Token:
        start_pos = self.position
        dot_count: int = 0

        output: str = ""
        while self.__is_digit(self.current_char) or self.current_char == '.':
            if self.current_char == '.':
                dot_count += 1

            if dot_count > 1:
                print(f"Too many decimals in number on line {self.line_no}, position {self.position}")
                return self.__new_token(TokenType.ILLEGAL, self.source[start_pos:self.position])

            output += self.source[self.position]
            self.__read_char()

            if self.current_char is None:
                break

        if dot_count == 0:
            return self.__new_token(TokenType.INT, int(output))
        else:
            return self.__new_token(TokenType.FLOAT, float(output))

    def __read_identifier(self) -> str:
        position = self.position
        while self.current_char is not None and (self.__is_letter(self.current_char) or self.current_char.isalnum()):
            self.__read_char()

        return self.source[position:self.position]

    def next_token(self) -> Token:
        tok: Token = None

        self.__skip_whitespace()
        match self.current_char:
            case '+':
                tok = self.__new_token(TokenType.PLUS, self.current_char)
            case '-':
                # Handle minus and arrow
                if self.__peek_char() == ">":
                    ch = self.current_char
                    self.__read_char()
                    tok = self.__new_token(TokenType.ARROW, ch + self.current_char)
                else:
                    tok = self.__new_token(TokenType.MINUS, self.current_char)
            case '*':
                # Handle power and multiplication
                if self.__peek_char() == "*":
                    ch = self.current_char
                    self.__read_char()
                    tok = self.__new_token(TokenType.POWER, ch + self.current_char)
                else:
                    tok = self.__new_token(TokenType.ASTERISK, self.current_char)
            case '/':
                tok = self.__new_token(TokenType.SLASH, self.current_char)
            case '%':
                tok = self.__new_token(TokenType.MODULUS, self.current_char)
            case '=':
                tok = self.__new_token(TokenType.EQ, self.current_char)
            case ':':
                tok = self.__new_token(TokenType.COLON, self.current_char)
            case '(':
                tok = self.__new_token(TokenType.LPAREN, self.current_char)
            case ')':
                tok = self.__new_token(TokenType.RPAREN, self.current_char)
            case '\n':
                tok = self.__new_token(TokenType.NEWLINE, "NEWLINE")
            case None:
                tok = self.__new_token(TokenType.EOF, "")
            case _:
                if self.__is_letter(self.current_char):
                    literal: str = self.__read_identifier()
                    tt: TokenType = lookup_identifier(literal)
                    tok = self.__new_token(tt, literal)
                    return tok
                elif self.__is_digit(self.current_char):
                    tok = self.__read_number()
                    return tok
                else:
                    tok = self.__new_token(TokenType.ILLEGAL, self.current_char)

        self.__read_char()
        return tok

