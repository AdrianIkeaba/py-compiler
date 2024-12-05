from Lexer import Lexer
from Token import Token, TokenType
from typing import Callable
from enum import Enum, auto

from AST import Statement, Expression, Program
from AST import ExpressionStatement, VariableStatement, FunctionStatement, ReturnStatement, BlockStatement, AssignStatement
from AST import InfixExpression, CallExpression
from AST import IntegerLiteral, FloatLiteral, IdentifierLiteral

class PrecedenceType(Enum):
    # Enum representing the precedence levels of different operations
    P_LOWEST = 0
    P_HIGHEST = auto()
    P_LESSGREATER = auto()
    P_SUM = auto()
    P_PRODUCT = auto()
    P_EXPONENT = auto()
    P_PREFIX = auto()
    P_CALL = auto()
    P_INDEX = auto()

# Mapping of token types to their corresponding precedence levels
PRECEDENCES: dict[TokenType, PrecedenceType] =  {
    TokenType.PLUS: PrecedenceType.P_SUM,
    TokenType.MINUS: PrecedenceType.P_SUM,
    TokenType.SLASH: PrecedenceType.P_PRODUCT,
    TokenType.ASTERISK: PrecedenceType.P_PRODUCT,
    TokenType.MODULUS: PrecedenceType.P_PRODUCT,
    TokenType.POWER: PrecedenceType.P_EXPONENT,
    TokenType.LPAREN: PrecedenceType.P_CALL,
}

class Parser:
    def __init__(self, lexer: Lexer) -> None:
        """Initializes the parser with a lexer and prepares for parsing."""
        self.lexer = lexer  # The lexer to tokenize the input

        self.errors: list[str] = []  # List to store parsing errors

        self.current_token: Token = None  # The current token being parsed
        self.peek_token: Token = None  # The next token to be parsed

        # Mapping of prefix parse functions for different token types
        self.prefix_parse_fns: dict[TokenType, Callable] = {
            TokenType.IDENTIFIER: self.__parse_identifier,
            TokenType.INT: self.__parse_int_literal,
            TokenType.FLOAT: self.__parse_float_literal,
            TokenType.LPAREN: self.__parse_grouped_expression,
        }
        # Mapping of infix parse functions for different token types
        self.infix_parse_fns: dict[TokenType, Callable] = {
            TokenType.PLUS: self.__parse_infix_expression,
            TokenType.MINUS: self.__parse_infix_expression,
            TokenType.SLASH: self.__parse_infix_expression,
            TokenType.ASTERISK: self.__parse_infix_expression,
            TokenType.POWER: self.__parse_infix_expression,
            TokenType.MODULUS: self.__parse_infix_expression,
            TokenType.LPAREN: self.__parse_call_expression,
        }

        # Initialize the current and peek tokens
        self.__next_token()
        self.__next_token()


    # Parse helpers region
    def __next_token(self) -> None:
        """Advances to the next token in the input."""
        self.current_token = self.peek_token  # Move current token to peek token
        self.peek_token = self.lexer.next_token()  # Get the next token from the lexer

    def __current_token_is(self, tt: TokenType) -> bool:
        """Checks if the current token is of the specified type."""
        return self.current_token.type == tt

    def __peek_token_is(self, tt: TokenType) -> bool:
        """Checks if the peek token is of the specified type."""
        return self.peek_token.type == tt

    def __expect_peek(self, tt: TokenType) -> bool:
        """Checks if the peek token is of the expected type and advances if true."""
        if self.__peek_token_is(tt):
            self.__next_token()  # Advance to the next token
            return True
        else:
            self.__peek_error(tt)  # Log an error if the expected token is not found
            return False

    def __current_precedence(self) -> PrecedenceType:
        """Returns the precedence of the current token."""
        prec: int | None = PRECEDENCES.get(self.current_token.type)
        if prec is None:
            return PrecedenceType.P_LOWEST  # Default to lowest precedence
        return prec

    def __peek_precedence(self) -> PrecedenceType:
        """Returns the precedence of the peek token."""
        prec: int | None = PRECEDENCES.get(self.peek_token.type)
        if prec is None:
            return PrecedenceType.P_LOWEST  # Default to lowest precedence
        return prec

    def __peek_error(self, tt: TokenType) -> None:
        """Logs an error if the expected token is not found."""
        self.errors.append(f"Expected next token {tt}, got {self.peek_token .type}")

    def __no_prefix_parse_fn_error(self, tt: TokenType):
        """Logs an error if no prefix parse function is found for the current token type."""
        self.errors.append(f"No prefix parse function found for '{tt}'")

    # end region

    def parse_program(self) -> None:
        """Parses the entire program and returns a Program node."""
        program: Program = Program()  # Create a new Program node

        while True:
            while self.__current_token_is(TokenType.NEWLINE):
                self.__next_token()  # Skip newline tokens

            if self.__current_token_is(TokenType.EOF):
                break  # End of file reached

            stmt: Statement = self.__parse_statement()  # Parse a statement
            if stmt is not None:
                program.statements.append(stmt)  # Add the statement to the program

            while self.__current_token_is(TokenType.NEWLINE):
                self.__next_token()  # Skip newline tokens

        return program  # Return the constructed program

    def __parse_statement(self) -> Statement:
        """Parses a statement based on the current token type."""
        while self.__current_token_is(TokenType.NEWLINE):
            self.__next_token()  # Skip newline tokens

        match self.current_token.type:
            case TokenType.IDENTIFIER:
                if self.__peek_token_is(TokenType.EQ):
                    return self.__parse_assign_statement()  # Parse assignment statement
                else:
                    return self.__parse_variable_statement()  # Parse variable statement
            case TokenType.DEF:
                return self.__parse_function_statement()  # Parse function statement
            case TokenType.RETURN:
                return self.__parse_return_statement()  # Parse return statement
            case _:
                return self.__parse_expression_statement()  # Parse expression statement

# Parse expression methods
    def __parse_expression_statement(self) -> ExpressionStatement:
        """Parses an expression statement."""
        expr = self.__parse_expression(PrecedenceType.P_LOWEST)  # Parse the expression

        if self.__peek_token_is(TokenType.NEWLINE):
            self.__next_token()  # Skip newline after the expression

        stmt: ExpressionStatement = ExpressionStatement(expr=expr)  # Create an ExpressionStatement node

        return stmt  # Return the statement

    def __parse_expression(self, precedence: PrecedenceType) -> Expression:
        """Parses an expression based on the current precedence level."""
        while self.__current_token_is(TokenType.NEWLINE):
            self.__next_token()  # Skip newline tokens

        prefix_fn: Callable | None = self.prefix_parse_fns.get(self.current_token.type)
        if prefix_fn is None:
            self.__no_prefix_parse_fn_error(self.current_token.type)  # Log error if no prefix function found
            return None

        left_expr: Expression = prefix_fn()  # Parse the left-hand side expression

        while not self.__peek_token_is(TokenType.EOF) and not self.__peek_token_is(
                TokenType.NEWLINE) and precedence.value < self.__peek_precedence().value:
            # Skip newline tokens during parsing
            while self.__peek_token_is(TokenType.NEWLINE):
                self.__next_token()

            infix_fn: Callable | None = self.infix_parse_fns.get(self.peek_token.type)
            if infix_fn is None:
                return left_expr  # Return the left expression if no infix function found

            self.__next_token()  # Advance to the infix operator token

            left_expr = infix_fn(left_expr)  # Parse the right-hand side expression

        return left_expr  # Return the complete expression

    def __parse_grouped_expression(self) -> Expression:
        """Parses an expression enclosed in parentheses."""
        self.__next_token()  # Skip the opening parenthesis

        expr: Expression = self.__parse_expression(PrecedenceType.P_LOWEST)  # Parse the enclosed expression

        if not self.__expect_peek(TokenType.RPAREN):
            return None  # Return None if the closing parenthesis is not found

        return expr  # Return the parsed expression

    def __parse_infix_expression(self, left_node: Expression) -> Expression:
        """Parses an infix expression with a left operand and an operator."""
        infix_expr: InfixExpression = InfixExpression(left_node=left_node, operator=self.current_token.literal)

        precedence = self.__current_precedence()  # Get the current precedence level

        self.__next_token()  # Advance to the operator token

        infix_expr.right_node = self.__parse_expression(precedence)  # Parse the right operand

        return infix_expr  # Return the infix expression

    def __parse_call_expression(self, function: Expression) -> CallExpression:
        """ Parses a function call expression with its arguments."""
        expr: CallExpression = CallExpression(function=function)  # Create a CallExpression node
        expr.arguments = []  # Initialize the arguments list (TODO: implement argument parsing)

        if not self.__expect_peek(TokenType.RPAREN):
            return None  # Return None if the closing parenthesis is not found

        return expr  # Return the parsed call expression

# End Region

    def __parse_variable_statement(self) -> VariableStatement:
        """Parses a variable declaration statement."""
        stmt: VariableStatement = VariableStatement()  # Create a VariableStatement node

        if not self.__current_token_is(TokenType.IDENTIFIER):
            return None  # Return None if the current token is not an identifier

        stmt.name = IdentifierLiteral(self.current_token.literal)  # Set the variable name

        if not self.__expect_peek(TokenType.COLON):
            return None  # Return None if the colon is not found

        if not self.__expect_peek(TokenType.TYPE):
            return None  # Return None if the type is not found

        stmt.value_type = self.current_token.literal  # Set the variable type

        if not self.__expect_peek(TokenType.EQ):
            return None  # Return None if the equals sign is not found

        self.__next_token()  # Advance to the value token

        stmt.value = self.__parse_expression(PrecedenceType.P_LOWEST)  # Parse the variable value

        while not self.__current_token_is(TokenType.NEWLINE) and not self.__current_token_is(TokenType.EOF):
            self.__next_token()  # Skip to the end of the statement

        return stmt  # Return the parsed variable statement

    def __parse_function_statement(self) -> FunctionStatement:
        """Parses a function declaration statement."""
        stmt: FunctionStatement = FunctionStatement()  # Create a FunctionStatement node

        if not self.__expect_peek(TokenType.IDENTIFIER):
            return None  # Return None if the function name is not found

        stmt.name = IdentifierLiteral(self.current_token.literal)  # Set the function name

        if not self.__expect_peek(TokenType.LPAREN):
            return None  # Return None if the opening parenthesis is not found

        stmt.parameters = []  # Initialize the parameters list (TODO: implement parameter parsing)
        if not self.__expect_peek(TokenType.RPAREN):
            return None  # Return None if the closing parenthesis is not found

        if not self.__expect_peek(TokenType.ARROW):
            return None  # Return None if the arrow is not found

        if not self.__expect_peek(TokenType.TYPE):
            return None  # Return None if the return type is not found

        stmt.return_type = self.current_token.literal  # Set the return type

        if not self.__expect_peek(TokenType.COLON):
            return None  # Return None if the colon is not found

        stmt.body = self.__parse_block_statement()  # Parse the function body

        return stmt  # Return the parsed function statement

    def __parse_return_statement(self) -> ReturnStatement:
        """Parses a return statement."""
        stmt: ReturnStatement = ReturnStatement()  # Create a ReturnStatement node

        self.__next_token()  # Advance to the return value token

        stmt.return_value = self.__parse_expression(PrecedenceType.P_LOWEST)  # Parse the return value

        if not self.__expect_peek(TokenType.NEWLINE):
            return None  # Return None if the newline is not found

        return stmt  # Return the parsed return statement

    def __parse_block_statement(self) -> BlockStatement:
        """Parses a block of statements."""
        block_stmt: BlockStatement = BlockStatement()  # Create a BlockStatement node

        self.__next_token()  # Advance to the first statement in the block

        while not self.__current_token_is(TokenType.EOF):
            stmt: Statement = self.__parse_statement()  # Parse a statement
            if stmt is not None:
                block_stmt.statements.append(stmt)  # Add the statement to the block

            self.__next_token()  # Advance to the next token

        return block_stmt  # Return the parsed block statement

    def __parse_assign_statement(self) -> AssignStatement:
        """Parses an assignment statement."""
        stmt: AssignStatement = AssignStatement()  # Create an AssignStatement node

        stmt.identifier = IdentifierLiteral(self.current_token.literal)  # Set the identifier for the assignment

        self.__next_token()  # Advance to the equals sign
        self.__next_token()  # Advance to the value token

        stmt.right_value = self.__parse_expression(PrecedenceType.P_LOWEST)  # Parse the right-hand side value

        self.__next_token()  # Advance to the next token

        return stmt  # Return the parsed assignment statement


    # Prefix Methods

    def __parse_identifier(self) -> Expression:
        """Parses an identifier and returns an IdentifierLiteral node."""
        return IdentifierLiteral(self.current_token.literal)  # Return the identifier as a node


    def __parse_int_literal(self) -> Expression:
        """Parses an IntegerLiteral node from the current token."""
        int_lit: IntegerLiteral = IntegerLiteral()  # Create an IntegerLiteral node

        try:
            int_lit.value = int(self.current_token.literal)  # Convert the literal to an integer
        except:
            self.errors.append(f"Could not parse '{self.current_token.literal}' as an integer")  # Log error
            return None

        return int_lit  # Return the parsed integer literal

    def __parse_float_literal(self) -> Expression:
        """Parses a FloatLiteral node from the current token."""
        float_lit: FloatLiteral = FloatLiteral()  # Create a FloatLiteral node

        try:
            float_lit.value = float(self.current_token.literal)  # Convert the literal to a float
        except:
            self.errors.append(f"Could not parse '{self.current_token.literal}' as a float")  # Log error
            return None

        return float_lit  # Return the parsed float literal
    # Region end