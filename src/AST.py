from abc import ABC, abstractmethod
from enum import Enum
from tkinter import Variable


class NodeType(Enum):
    Program = "Program"

    # Statements
    ExpressionStatement = "ExpressionStatement"
    VariableStatement = "VariableStatement"
    FunctionStatement = "FunctionStatement"
    BlockStatement = "BlockStatement"
    ReturnStatement = "ReturnStatement"
    AssignStatement = "AssignStatement"

    # Expression
    InfixExpression = "InfixExpression"
    CallExpression = "CallExpression"

    # Literals
    IntegerLiteral = "IntegerLiteral"
    FloatLiteral = "FloatLiteral"
    IdentifierLiteral = "IdentifierLiteral"

class Node(ABC):
    @abstractmethod
    def type(self) -> NodeType:
        pass

    @abstractmethod
    def json(self) -> dict:
        pass


class Statement(Node):
    pass

class Expression(Node):
    pass

class Program(Node):
    def __init__(self) -> None:
        self.statements: list[Statement] = []

    def type(self) -> NodeType:
        return NodeType.Program

    def json(self) -> dict:
        return {
            "type": self.type().value,
            "statements": [{stmt.type().value: stmt.json()} for stmt in self.statements]
        }

# Statements Region
class ExpressionStatement(Statement):
    def __init__(self, expr: Expression = None) -> None:
        self.expr = expr

    def type(self) -> NodeType:
        return NodeType.ExpressionStatement

    def json(self) -> dict:
        return {
            "type": self.type().value,
            "expr": self.expr.json()
        }

class CallExpression(Expression):
    def __init__(self, function: Expression = None, arguments: list[Expression] = None) -> None:
        self.function = function
        self.arguments = arguments

    def type(self) -> NodeType:
        return NodeType.CallExpression

    def json(self) -> dict:
        return {
            "type": self.type().value,
            "function": self.function.json(),
            "arguments": [arg.json() for arg in self.arguments]
        }
#End region


class VariableStatement(Statement):
    def __init__(self, name: Expression = None, value: Expression = None, value_type: str = None) -> None:
        self.name = name
        self.value = value
        self.value_type = value_type

    def type(self) -> NodeType:
        return NodeType.VariableStatement

    def json(self) -> dict:
        return {
            "type": self.type().value,
            "name": self.name.json(),
            "value": self.value.json(),
            "value_type": self.value_type
        }

class BlockStatement(Statement):
    def __init__(self, statements: list[Statement] = None) -> None:
        self.statements = statements if statements is not None else []

    def type(self) -> NodeType:
        return NodeType.BlockStatement

    def json(self) -> dict:
        return {
            "type": self.type().value,
            "statements": [stmt.json() for stmt in self.statements]
        }

class ReturnStatement(Statement):
    def __init__(self, return_value: Expression = None) -> None:
        self.return_value = return_value

    def type(self) -> NodeType:
        return NodeType.ReturnStatement

    def json(self) -> dict:
        return {
            "type": self.type().value,
            "return_value": self.return_value.json()
        }

class FunctionStatement(Statement):
    def __init__(self, parameters: list = [], body: BlockStatement = None, name = None, return_type: str = None) -> None:
        self.parameters = parameters
        self.body = body
        self.name = name
        self.return_type = return_type

    def type(self) -> NodeType:
        return NodeType.FunctionStatement

    def json(self) -> dict:
        return {
            "type": self.type().value,
            "name": self.name.json(),
            "return_type": self.return_type,
            "parameters": [p.json() for p in self.parameters],
            "body": self.body.json(),
        }

class AssignStatement(Statement):
    def __init(self, identifier: Expression = None, right_value: Expression = None) -> None:
        self.identifier = identifier
        self.right_value = right_value

    def type(self) -> NodeType:
        return NodeType.AssignStatement

    def json(self) -> dict:
        return {
            "type": self.type().value,
            "identifier": self.identifier.json(),
            "right_value": self.right_value.json()
        }
# End region


# Expression Region
class InfixExpression(Expression):
    def __init__(self, left_node: Expression, operator: str, right_node = None) -> None:
        self.left_node: Expression = left_node
        self.operator: str = operator
        self.right_node: Expression = right_node


    def type(self) -> NodeType:
        return NodeType.InfixExpression

    def json(self) -> dict:
        return {
            "type": self.type().value,
            "left_node": self.left_node.json(),
            "operator": self.operator,
            "right_node": self.right_node.json()
        }

# End region


# Literal Region
class IntegerLiteral(Expression):
    def __init__(self, value: int = None) -> None:
        self.value: int = value

    def type(self) -> NodeType:
        return NodeType.IntegerLiteral

    def json(self) -> dict:
        return {
            "type": self.type().value,
            "value": self.value
        }


class FloatLiteral(Expression):
    def __init__(self, value: float = None) -> None:
        self.value: float = value

    def type(self) -> NodeType:
        return NodeType.FloatLiteral

    def json(self) -> dict:
        return {
            "type": self.type().value,
            "value": self.value
        }

class IdentifierLiteral(Expression):
    def __init__(self, value: str = None) -> None:
        self.value: str = value

    def type(self) -> NodeType:
        return NodeType.IdentifierLiteral

    def json(self) -> dict:
        return {
            "type": self.type().value,
            "value": self.value
        }
# End region
