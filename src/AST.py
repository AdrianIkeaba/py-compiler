from abc import ABC, abstractmethod
from enum import Enum


class NodeType(Enum):
    # Enum representing different types of nodes in the Abstract Syntax Tree (AST)
    Program = "Program"

    # Statements
    ExpressionStatement = "ExpressionStatement"
    VariableStatement = "VariableStatement"
    FunctionStatement = "FunctionStatement"
    BlockStatement = "BlockStatement"
    ReturnStatement = "ReturnStatement"
    AssignStatement = "AssignStatement"
    PrintStatement = "PrintStatement"  # Add PrintStatement type

    # Expression
    InfixExpression = "InfixExpression"
    CallExpression = "CallExpression"

    # Literals
    IntegerLiteral = "IntegerLiteral"
    FloatLiteral = "FloatLiteral"
    IdentifierLiteral = "IdentifierLiteral"
    StringLiteral = "StringLiteral"  # Add StringLiteral type


class Node(ABC):
    @abstractmethod
    def type(self) -> NodeType:
        """Returns the type of the node."""
        pass

    @abstractmethod
    def json(self) -> dict:
        """Returns a JSON representation of the node."""
        pass


class Statement(Node):
    """Base class for all statement nodes in the AST."""
    pass

class Expression(Node):
    """Base class for all expression nodes in the AST."""
    pass

class Program(Node):
    def __init__(self) -> None:
        """Initializes a Program node with an empty list of statements."""
        self.statements: list[Statement] = []  # List to hold statements in the program

    def type(self) -> NodeType:
        """Returns the type of the node as NodeType.Program."""
        return NodeType.Program

    def json(self) -> dict:
        """Returns a JSON representation of the Program node."""
        return {
            "type": self.type().value,
            "statements": [{stmt.type().value: stmt.json()} for stmt in self.statements]  # Convert each statement to JSON
        }

# Statements Region
class ExpressionStatement(Statement):
    def __init__(self, expr: Expression = None) -> None:
        """Initializes an ExpressionStatement node with an expression."""
        self.expr = expr  # The expression contained in this statement

    def type(self) -> NodeType:
        """Returns the type of the node as NodeType.ExpressionStatement."""
        return NodeType.ExpressionStatement

    def json(self) -> dict:
        """Returns a JSON representation of the ExpressionStatement node."""
        return {
            "type": self.type().value,
            "expr": self.expr.json()  # Convert the expression to JSON
        }

class PrintStatement(Statement):
    def __init__(self, value: Expression) -> None:
        """Initializes a PrintStatement node with a value to print."""
        self.value = value  # The value to be printed

    def type(self) -> NodeType:
        """Returns the type of the node as NodeType.PrintStatement."""
        return NodeType.PrintStatement

    def json(self) -> dict:
        """Returns a JSON representation of the PrintStatement node."""
        return {
            "type": self.type().value,
            "value": self.value.json()  # Convert the value to JSON
        }

class CallExpression(Expression):
    def __init__(self, function: Expression = None, arguments: list[Expression] = None) -> None:
        """Initializes a CallExpression node with a function and its arguments."""
        self.function = function  # The function being called
        self.arguments = arguments  # List of arguments for the function call

    def type(self) -> NodeType:
        """Returns the type of the node as NodeType.CallExpression."""
        return NodeType.CallExpression

    def json(self) -> dict:
        """Returns a JSON representation of the CallExpression node."""
        return {
            "type": self.type().value,
            "function": self.function.json(),  # Convert the function to JSON
            "arguments": [arg.json() for arg in self.arguments]  # Convert each argument to JSON
        }
# End region


class VariableStatement(Statement):
    def __init__(self, name: Expression = None, value: Expression = None, value_type: str = None) -> None:
        """Initializes a VariableStatement node with a name, value, and type."""
        self.name = name  # The name of the variable
        self.value = value  # The value assigned to the variable
        self.value_type = value_type  # The type of the variable (e.g., int, float)

    def type(self) -> NodeType:
        """Returns the type of the node as NodeType.VariableStatement."""
        return NodeType.VariableStatement

    def json(self) -> dict:
        """Returns a JSON representation of the VariableStatement node."""
        return {
            "type": self.type().value,
            "name": self.name.json(),  # Convert the name to JSON
            "value": self.value.json(),  # Convert the value to JSON
            "value_type": self.value_type  # Include the variable type
        }

class BlockStatement(Statement):
    def __init__(self, statements: list[Statement] = None) -> None:
        """Initializes a BlockStatement node with a list of statements."""
        self.statements = statements if statements is not None else []  # List of statements in the block

    def type(self) -> NodeType:
        """Returns the type of the node as NodeType.BlockStatement."""
        return NodeType.BlockStatement

    def json(self) -> dict:
        """Returns a JSON representation of the BlockStatement node."""
        return {
            "type": self.type().value,
            "statements": [stmt.json() for stmt in self.statements]  # Convert each statement in the block to JSON
        }

class ReturnStatement(Statement):
    def __init__(self, return_value: Expression = None) -> None:
        """Initializes a ReturnStatement node with a return value."""
        self.return_value = return_value  # The value to be returned

    def type(self) -> NodeType:
        """Returns the type of the node as NodeType.ReturnStatement."""
        return NodeType.ReturnStatement

    def json(self) -> dict:
        """Returns a JSON representation of the ReturnStatement node."""
        return {
            "type": self.type().value,
            "return_value": self.return_value.json()  # Convert the return value to JSON
        }

class FunctionStatement(Statement):
    def __init__(self, parameters: list = [], body: BlockStatement = None, name = None, return_type: str = None) -> None:
        """Initializes a FunctionStatement node with parameters, body, name, and return type."""
        self.parameters = parameters  # List of parameters for the function
        self.body = body  # The body of the function as a BlockStatement
        self.name = name  # The name of the function
        self.return_type = return_type  # The return type of the function

    def type(self) -> NodeType:
        """Returns the type of the node as NodeType.FunctionStatement."""
        return NodeType.FunctionStatement

    def json(self) -> dict:
        """Returns a JSON representation of the FunctionStatement node."""
        return {
            "type": self.type().value,
            "name": self.name.json(),  # Convert the function name to JSON
            "return_type": self.return_type,  # Include the return type
            "parameters": [p.json() for p in self.parameters],  # Convert each parameter to JSON
            "body": self.body.json(),  # Convert the body to JSON
        }

class AssignStatement(Statement):
    def __init__(self, identifier: Expression = None, right_value: Expression = None) -> None:
        """Initializes an AssignStatement node with an identifier and a right-hand side value."""
        self.identifier = identifier  # The variable being assigned to
        self.right_value = right_value  # The value being assigned

    def type(self) -> NodeType:
        """Returns the type of the node as NodeType.AssignStatement."""
        return NodeType.AssignStatement

    def json(self) -> dict:
        """Returns a JSON representation of the AssignStatement node."""
        return {
            "type": self.type().value,
            "identifier": self.identifier.json(),  # Convert the identifier to JSON
            "right_value": self.right_value.json()  # Convert the right-hand side value to JSON
        }
# End region


# Expression Region
class InfixExpression(Expression):
    def __init__(self, left_node: Expression, operator: str, right_node: Expression = None) -> None:
        """Initializes an InfixExpression node with left and right operands and an operator."""
        self.left_node: Expression = left_node  # The left operand
        self.operator: str = operator  # The operator (e.g., +, -, *, /)
        self.right_node: Expression = right_node  # The right operand

    def type(self) -> NodeType:
        """Returns the type of the node as NodeType.InfixExpression."""
        return NodeType.InfixExpression

    def json(self) -> dict:
        """Returns a JSON representation of the InfixExpression node."""
        return {
            "type": self.type().value,
            "left_node": self.left_node.json(),  # Convert the left operand to JSON
            "operator": self.operator,  # Include the operator
            "right_node": self.right_node.json() if self.right_node else None  # Convert the right operand to JSON
        }
# End region


# Literal Region
class IntegerLiteral(Expression):
    def __init__(self, value: int = None) -> None:
        """Initializes an IntegerLiteral node with a value."""
        self.value: int = value  # The integer value

    def type(self) -> NodeType:
        """Returns the type of the node as NodeType.IntegerLiteral."""
        return NodeType.IntegerLiteral

    def json(self) -> dict:
        """Returns a JSON representation of the IntegerLiteral node."""
        return {
            "type": self.type().value,
            "value": self.value  # Include the integer value
        }


class FloatLiteral(Expression):
    def __init__(self, value: float = None) -> None:
        """Initializes a FloatLiteral node with a value."""
        self.value: float = value  # The float value

    def type(self) -> NodeType:
        """Returns the type of the node as NodeType.FloatLiteral."""
        return NodeType.FloatLiteral

    def json(self) -> dict:
        """Returns a JSON representation of the FloatLiteral node."""
        return {
            "type": self.type().value,
            "value": self.value  # Include the float value
        }

class IdentifierLiteral(Expression):
    def __init__(self, value: str = None) -> None:
        """Initializes an IdentifierLiteral node with a value."""
        self.value: str = value  # The identifier value

    def type(self) -> NodeType:
        """Returns the type of the node as NodeType.IdentifierLiteral."""
        return NodeType.IdentifierLiteral

    def json(self) -> dict:
        """Returns a JSON representation of the IdentifierLiteral node."""
        return {
            "type": self.type().value,
            "value": self.value  # Include the identifier value
        }

class StringLiteral(Expression):
    def __init__(self, value: str = None) -> None:
        """Initializes a StringLiteral node with a value."""
        self.value: str = value  # The string value

    def type(self) -> NodeType:
        """Returns the type of the node as NodeType.StringLiteral."""
        return NodeType.StringLiteral

    def json(self) -> dict:
        """Returns a JSON representation of the StringLiteral node."""
        return {
            "type": self.type().value,
            "value": self.value  # Include the string value
        }