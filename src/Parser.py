from Lexer import Lexer
from Token import Token, TokenType
from typing import Callable
from enum import Enum, auto

from AST import Statement, Expression, Program
from AST import ExpressionStatement, VariableStatement, FunctionStatement, ReturnStatement, BlockStatement, AssignStatement
from AST import InfixExpression, CallExpression
from AST import IntegerLiteral, FloatLiteral, IdentifierLiteral

class PrecedenceType(Enum):
    P_LOWEST = 0
    P_HIGHEST = auto()
    P_LESSGREATER = auto()
    P_SUM = auto()
    P_PRODUCT = auto()
    P_EXPONENT = auto()
    P_PREFIX = auto()
    P_CALL = auto()
    P_INDEX = auto()

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
        self.lexer = lexer

        self.errors: list[str] = []

        self.current_token: Token = None
        self.peek_token: Token = None

        self.prefix_parse_fns: dict[TokenType, Callable] = {
            TokenType.IDENTIFIER: self.__parse_identifier,
            TokenType.INT: self.__parse_int_literal,
            TokenType.FLOAT: self.__parse_float_literal,
            TokenType.LPAREN: self.__parse_grouped_expression,
        }
        self.infix_parse_fns: dict[TokenType, Callable] = {
            TokenType.PLUS: self.__parse_infix_expression,
            TokenType.MINUS: self.__parse_infix_expression,
            TokenType.SLASH: self.__parse_infix_expression,
            TokenType.ASTERISK: self.__parse_infix_expression,
            TokenType.POWER: self.__parse_infix_expression,
            TokenType.MODULUS: self.__parse_infix_expression,
            TokenType.LPAREN: self.__parse_call_expression,
        }

        self.__next_token()
        self.__next_token()


    # Parse helpers region
    def __next_token(self) -> None:
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def __current_token_is(self, tt: TokenType) -> bool:
        return self.current_token.type == tt

    def __peek_token_is(self, tt: TokenType) -> bool:
        return self.peek_token.type == tt

    def __expect_peek(self, tt: TokenType) -> bool:
        if self.__peek_token_is(tt):
            self.__next_token()
            return True
        else:
            self.__peek_error(tt)
            return False

    def __current_precedence(self) -> PrecedenceType:
        prec: int | None = PRECEDENCES.get(self.current_token.type)
        if prec is None:
            return PrecedenceType.P_LOWEST
        return prec

    def __peek_precedence(self) -> PrecedenceType:
        prec: int | None = PRECEDENCES.get(self.peek_token.type)
        if prec is None:
            return PrecedenceType.P_LOWEST
        return prec

    def __peek_error(self, tt: TokenType) -> None:
        self.errors.append(f"Expected next token {tt}, got {self.peek_token.type}")

    def __no_prefix_parse_fn_error(self, tt: TokenType):
        self.errors.append(f"No prefix parse function found for '{tt}'")

    # end region

    def parse_program(self) -> None:
        program: Program = Program()

        while True:
            while self.__current_token_is(TokenType.NEWLINE):
                self.__next_token()

            if self.__current_token_is(TokenType.EOF):
                break

            stmt: Statement = self.__parse_statement()
            if stmt is not None:
                program.statements.append(stmt)

            while self.__current_token_is(TokenType.NEWLINE):
                self.__next_token()

        return program

    def __parse_statement(self) -> Statement:
        while self.__current_token_is(TokenType.NEWLINE):
            self.__next_token()


        match self.current_token.type:
            case TokenType.IDENTIFIER:
                if self.__peek_token_is(TokenType.EQ):
                    return self.__parse_assign_statement()
                else:
                    return self.__parse_variable_statement()
            case TokenType.DEF:
                return self.__parse_function_statement()
            case TokenType.RETURN:
                return self.__parse_return_statement()
            case _:
                return self.__parse_expression_statement()

# Parse expression methods
    def __parse_expression_statement(self) -> ExpressionStatement:
        expr = self.__parse_expression(PrecedenceType.P_LOWEST)

        if self.__peek_token_is(TokenType.NEWLINE):
            self.__next_token()

        stmt: ExpressionStatement = ExpressionStatement(expr=expr)

        return stmt

    def __parse_expression(self, precedence: PrecedenceType) -> Expression:
        while self.__current_token_is(TokenType.NEWLINE):
            self.__next_token()

        prefix_fn: Callable | None = self.prefix_parse_fns.get(self.current_token.type)
        if prefix_fn is None:
            self.__no_prefix_parse_fn_error(self.current_token.type)
            return None

        left_expr: Expression = prefix_fn()

        while not self.__peek_token_is(TokenType.EOF) and not self.__peek_token_is(
                TokenType.NEWLINE) and precedence.value < self.__peek_precedence().value:
            # Skip newline tokens during parsing
            while self.__peek_token_is(TokenType.NEWLINE):
                self.__next_token()

            infix_fn: Callable | None = self.infix_parse_fns.get(self.peek_token.type)
            if infix_fn is None:
                return left_expr

            self.__next_token()

            left_expr = infix_fn(left_expr)

        return left_expr

    def __parse_grouped_expression(self) -> Expression:
        self.__next_token()

        expr: Expression = self.__parse_expression(PrecedenceType.P_LOWEST)

        if not self.__expect_peek(TokenType.RPAREN):
            return None

        return expr

    def __parse_infix_expression(self, left_node: Expression) -> Expression:
        infix_expr: InfixExpression = InfixExpression(left_node=left_node, operator=self.current_token.literal)

        precedence = self.__current_precedence()

        self.__next_token()

        infix_expr.right_node = self.__parse_expression(precedence)

        return infix_expr

    def __parse_call_expression(self, function: Expression) -> CallExpression:
        expr: CallExpression = CallExpression(function=function)
        expr.arguments = [] # TODO

        if not self.__expect_peek(TokenType.RPAREN):
            return None

        return expr

# End Region

    def __parse_variable_statement(self) -> VariableStatement:
        # age: int = 20
        stmt: VariableStatement = VariableStatement()

        if not self.__current_token_is(TokenType.IDENTIFIER):
            return None

        stmt.name = IdentifierLiteral(self.current_token.literal)

        if not self.__expect_peek(TokenType.COLON):
            return None

        if not self.__expect_peek(TokenType.TYPE):
            return None

        stmt.value_type = self.current_token.literal

        if not self.__expect_peek(TokenType.EQ):
            return None

        self.__next_token()

        stmt.value = self.__parse_expression(PrecedenceType.P_LOWEST)

        while not self.__current_token_is(TokenType.NEWLINE) and not self.__current_token_is(TokenType.EOF):
            self.__next_token()

        return stmt

    def __parse_function_statement(self) -> FunctionStatement:
        stmt: FunctionStatement = FunctionStatement()
        # def main() -> int:

        if not self.__expect_peek(TokenType.IDENTIFIER):
            return None

        stmt.name = IdentifierLiteral(self.current_token.literal)

        if not self.__expect_peek(TokenType.LPAREN):
            return None

        stmt.parameters = [] # TODO
        if not self.__expect_peek(TokenType.RPAREN):
            return None

        if not self.__expect_peek(TokenType.ARROW):
            return None

        if not self.__expect_peek(TokenType.TYPE):
            return None

        stmt.return_type = self.current_token.literal

        if not self.__expect_peek(TokenType.COLON):
            return None

        stmt.body = self.__parse_block_statement()

        return stmt


    def __parse_return_statement(self) -> ReturnStatement:
        stmt: ReturnStatement = ReturnStatement()

        self.__next_token()

        stmt.return_value = self.__parse_expression(PrecedenceType.P_LOWEST)

        if not self.__expect_peek(TokenType.NEWLINE):
            return None

        return stmt

    def __parse_block_statement(self) -> BlockStatement:
        block_stmt: BlockStatement = BlockStatement()

        self.__next_token()

        while not self.__current_token_is(TokenType.EOF):
            stmt: Statement = self.__parse_statement()
            if stmt is not None:
                block_stmt.statements.append(stmt)

            self.__next_token()

        return block_stmt

    def __parse_assign_statement(self) -> AssignStatement:
        stmt: AssignStatement = AssignStatement()

        stmt.identifier = IdentifierLiteral(self.current_token.literal)

        self.__next_token()
        self.__next_token()

        stmt.right_value = self.__parse_expression(PrecedenceType.P_LOWEST)

        self.__next_token()

        return stmt



    # Prefix Methods

    def __parse_identifier(self) -> Expression:
        return IdentifierLiteral(self.current_token.literal)


    def __parse_int_literal(self) -> Expression:
        """Parses an IntegerLiteral node from the current token"""
        int_lit: IntegerLiteral = IntegerLiteral()

        try:
            int_lit.value = int(self.current_token.literal)
        except:
            self.errors.append(f"Could not parse '{self.current_token.literal}' as an integer")
            return None

        return int_lit

    def __parse_float_literal(self) -> Expression:
        """Parses a FloatLiteral node from the current token"""
        float_lit: FloatLiteral = FloatLiteral()

        try:
            float_lit.value = float(self.current_token.literal)
        except:
            self.errors.append(f"Could not parse '{self.current_token.literal}' as a float")
            return None

        return float_lit
    # Region end