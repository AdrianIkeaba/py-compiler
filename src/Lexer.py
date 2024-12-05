from typing import Any

from Token import Token
from Token import TokenType
from Token import lookup_identifier


class Lexer:
    def __init__(self, source: str) -> None:
        """
        Initializes the Lexer with the provided source code.

        Args:
            source (str): The source code to be tokenized.
        """
        self.source = source  # The source code to tokenize

        self.position: int = 0  # Current position in the source code
        self.read_position: int = 0  # Position to read the next character
        self.line_no: int = 1  # Current line number

        self.current_char: str | None = None  # Current character being processed

        self.__read_char()  # Read the first character

    def __read_char(self) -> None:
        """
        Reads the next character from the source code and updates the position.
        """
        if self.read_position >= len(self.source):
            self.current_char = None  # End of source
        else:
            self.current_char = self.source[self.read_position]  # Get the current character

        self.position = self.read_position  # Update the current position
        self.read_position += 1  # Move to the next character

    def __peek_char(self) -> str | None:
        """
        Peeks to the upcoming char without advancing the lexer.

        Returns:
            str | None: The next character or None if at the end of the source.
        """
        if self.read_position >= len(self.source):
            return None  # Return None if at the end of the source

        return self.source[self.read_position]  # Return the next character

    def __skip_whitespace(self) -> None:
        """
        Skips whitespace characters in the source code and updates the line number.
        """
        while self.current_char in [' ', '\t', '\r']:  # While current character is whitespace
            if self.current_char == '\n':
                self.line_no += 1  # Increment line number on newline

            self.__read_char()  # Read the next character

    def __new_token(self, tt: TokenType, literal: Any) -> Token:
        """
        Creates a new token with the specified type and literal value.

        Args:
            tt (TokenType): The type of the token.
            literal (Any): The literal value of the token.

        Returns:
            Token: The newly created token.
        """
        return Token(type=tt, literal=literal, line_no=self.line_no, position=self.position)

    def __is_digit(self, ch: str) -> bool:
        """
        Checks if the character is a digit.

        Args:
            ch (str): The character to check.

        Returns:
            bool: True if the character is a digit, False otherwise.
        """
        return '0' <= ch <= '9'  # Check if character is between '0' and '9'

    def __is_letter(self, ch: str) -> bool:
        """
        Checks if the character is a letter or underscore.

        Args:
            ch (str): The character to check.

        Returns:
            bool: True if the character is a letter or underscore, False otherwise.
        """
        return 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or ch == '_'  # Check for letters and underscore

    def __read_number(self) -> Token:
        """
        Reads a number (integer or float) from the source code.

        Returns:
            Token: The token representing the number.
        """
        start_pos = self.position  # Store the starting position of the number
        dot_count: int = 0  # Count of decimal points in the number

        output: str = ""  # String to accumulate the number
        while self.__is_digit(self.current_char) or self.current_char == '.':
            if self.current_char == '.':
                dot_count += 1  # Increment dot count for float numbers

            if dot_count > 1:
                print(f"Too many decimals in number on line {self.line_no}, position {self.position}")
                return self.__new_token(TokenType.ILLEGAL, self.source[start_pos:self.position])  # Return illegal token

            output += self.source[self.position]  # Append current character to output
            self.__read_char()  # Read the next character

            if self.current_char is None:
                break  # End of source

        # Determine if the number is an integer or float based on dot count
        if dot_count == 0:
            return self.__new_token(TokenType.INT, int(output))  # Return integer token
        else:
            return self.__new_token(TokenType.FLOAT, float(output ))  # Return float token

    def __read_identifier(self) -> str:
        """
        Reads an identifier (variable name) from the source code.

        Returns:
            str: The identifier string.
        """
        position = self.position  # Store the starting position of the identifier
        while self.current_char is not None and (self.__is_letter(self.current_char) or self.current_char.isalnum()):
            self.__read_char()  # Read the next character

        return self.source[position:self.position]  # Return the identifier string

    def next_token(self) -> Token:
        """
        Retrieves the next token from the source code.

        Returns:
            Token: The next token.
        """
        tok: Token = None  # Initialize token variable

        self.__skip_whitespace()  # Skip any whitespace characters
        match self.current_char:  # Match the current character
            case '+':
                tok = self.__new_token(TokenType.PLUS, self.current_char)  # Create plus token
            case '-':
                # Handle minus and arrow
                if self.__peek_char() == ">":
                    ch = self.current_char  # Store current character
                    self.__read_char()  # Read the next character
                    tok = self.__new_token(TokenType.ARROW, ch + self.current_char)  # Create arrow token
                else:
                    tok = self.__new_token(TokenType.MINUS, self.current_char)  # Create minus token
            case '*':
                # Handle power and multiplication
                if self.__peek_char() == "*":
                    ch = self.current_char  # Store current character
                    self.__read_char()  # Read the next character
                    tok = self.__new_token(TokenType.POWER, ch + self.current_char)  # Create power token
                else:
                    tok = self.__new_token(TokenType.ASTERISK, self.current_char)  # Create multiplication token
            case '/':
                tok = self.__new_token(TokenType.SLASH, self.current_char)  # Create division token
            case '%':
                tok = self.__new_token(TokenType.MODULUS, self.current_char)  # Create modulus token
            case '=':
                tok = self.__new_token(TokenType.EQ, self.current_char)  # Create equality token
            case ':':
                tok = self.__new_token(TokenType.COLON, self.current_char)  # Create colon token
            case '(':
                tok = self.__new_token(TokenType.LPAREN, self.current_char)  # Create left parenthesis token
            case ')':
                tok = self.__new_token(TokenType.RPAREN, self.current_char)  # Create right parenthesis token
            case '\n':
                tok = self.__new_token(TokenType.NEWLINE, "NEWLINE")  # Create newline token
            case None:
                tok = self.__new_token(TokenType.EOF, "")  # Create end of file token
            case _:
                if self.__is_letter(self.current_char):
                    literal: str = self.__read_identifier()  # Read identifier
                    tt: TokenType = lookup_identifier(literal)  # Lookup token type for identifier
                    tok = self.__new_token(tt, literal)  # Create token for identifier
                    return tok
                elif self.__is_digit(self.current_char):
                    return self.__read_number()  # Read number token
                else:
                    tok = self.__new_token(TokenType.ILLEGAL, self.current_char)  # Create illegal token

        self.__read_char()  # Read the next character for the next token
        return tok  # Return the token