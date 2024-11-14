from llvmlite import ir

from AST import  NodeType, Expression, Program, Node
from AST import ExpressionStatement, VariableStatement, IdentifierLiteral, BlockStatement, FunctionStatement, ReturnStatement, AssignStatement
from AST import InfixExpression, CallExpression
from AST import IntegerLiteral, FloatLiteral

from Environment import Environment

class Compiler:
    def __init__(self) -> None:
        self.type_map: dict[str, ir.Type] = {
            'int': ir.IntType(32),
            'float': ir.FloatType(),
        }

        self.module: ir.Module = ir.Module('main')

        self.builder: ir.IRBuilder = ir.IRBuilder()

        self.env: Environment = Environment()

        self.errors: list[str] = []

    def compile(self, node: Node) -> None:
        match node.type():
            case NodeType.Program:
                self.__visit_program(node)

            case NodeType.VariableStatement:
                self.__visit_variable_statement(node)
            case NodeType.ExpressionStatement:
                self.__visit_expression_statement(node)
            case NodeType.BlockStatement:
                self.__visit_block_statement(node)
            case NodeType.FunctionStatement:
                self.__visit_function_statement(node)
            case NodeType.ReturnStatement:
                self.__visit_return_statement(node)
            case NodeType.AssignStatement:
                self.__visit_assign_statement(node)


            case NodeType.InfixExpression:
                self.__visit_infix_expression(node)
            case NodeType.CallExpression:
                self.__visit_call_expression(node)

    def __visit_program(self, node: Program) -> None:
        for stmt in node.statements:
            self.compile(stmt)

    def __visit_expression_statement(self, node: ExpressionStatement) -> None:
        self.compile(node.expr)

    def __visit_variable_statement(self, node: VariableStatement) -> None:
        name: str = node.name.value
        value: Expression = node.value
        value_type: str = node.value_type # TODO

        value, Type = self.__resolve_value(value)

        if self.env.lookup(name) is None:
            llvm_type = self.type_map.get(value_type, None)
            if llvm_type is None:
                self.errors.append(f"Unknown type '{value_type}' for variable '{name}'.")
                return

            ptr = self.builder.alloca(llvm_type, name=name)

            self.builder.store(value, ptr)

            self.env.define(name, ptr, Type)
        else:
            ptr, _ = self.env.lookup(name)
            self.builder.store(value, ptr)


    def __visit_block_statement(self, node: BlockStatement) -> None:
        for stmt in node.statements:
            self.compile(stmt)


    def __visit_return_statement(self, node: ReturnStatement) -> None:
        value: Expression = node.return_value
        value, Type = self.__resolve_value(value)

        self.builder.ret(value)

    def __visit_function_statement(self, node: FunctionStatement) -> None:
        name: str = node.name.value
        body: BlockStatement = node.body
        params: list[IdentifierLiteral] = node.parameters

        param_names: list[str] = [p.value.name for p in params]

        param_types: list[ir.Type] = [] # TODO

        return_type: ir.Type = self.type_map[node.return_type]

        fnty: ir.FunctionType = ir.FunctionType(return_type, param_types)
        func: ir.Function = ir.Function(self.module, fnty, name)

        block = ir.Block = func.append_basic_block(f"{name}_entry")

        previous_builder = self.builder

        self.builder = ir.IRBuilder(block)

        previous_env = self.env

        self.env = Environment(parent=self.env)
        self.env.define(name, func, return_type)

        self.compile(body)

        self.env = previous_env
        self.env.define(name, func, return_type)

        self.builder = previous_builder

    def __visit_assign_statement(self, node: AssignStatement) -> None:
        name: str = node.identifier.value
        value: Expression = node.right_value

        value, Type = self.__resolve_value(value)

        if self.env.lookup(name) is None:
            self.errors.append(f"Compile Error: {name} has not been declared.")
        else:
            ptr,_ = self.env.lookup(name)
            self.builder.store(value, ptr)


    def __visit_infix_expression(self, node: InfixExpression) -> None:
        operator: str = node.operator
        left_value, left_type = self.__resolve_value(node.left_node)
        right_value, right_type = self.__resolve_value(node.right_node)

        value = None
        Type = None

        if isinstance(right_type, ir.IntType) and isinstance(left_type, ir.IntType):
            Type = self.type_map["int"]
            match operator:
                case '+':
                    value = self.builder.add(left_value, right_value)
                case '-':
                    value = self.builder.sub(left_value, right_value)
                case '*':
                    value = self.builder.mul(left_value, right_value)
                case '/':
                    value = self.builder.sdiv(left_value, right_value)
                case '%':
                    value = self.builder.srem(left_value, right_value)
                case '**':
                    #TODO
                    pass
        elif isinstance(right_type, ir.FloatType) and isinstance(left_type, ir.FloatType):
            Type = ir.FloatType()
            match operator:
                case '+':
                    value = self.builder.fadd(left_value, right_value)
                case '-':
                    value = self.builder.fsub(left_value, right_value)
                case '*':
                    value = self.builder.fmul(left_value, right_value)
                case '/':
                    value = self.builder.fdiv(left_value, right_value)
                case '%':
                    value = self.builder.frem(left_value, right_value)
                case '**':
                    # TODO
                    pass

        return value, Type

    def __visit_call_expression(self, node: CallExpression) -> None:
        name: str = node.function.value
        params: list[Expression] = node.arguments

        args = []
        types = []
        # TODO

        match name:
            case _:
                func, ret_type = self.env.lookup(name)
                ret = self.builder.call(func, args)

        return ret, ret_type


    def __resolve_value(self, node: Expression) -> tuple[ir.Value, ir.Type]:
        match node.type():
            case NodeType.IntegerLiteral:
                node: IntegerLiteral = node
                value, Type = node.value, self.type_map["int"]
                return ir.Constant(Type, value), Type
            case NodeType.FloatLiteral:
                node: FloatLiteral = node
                value, Type = node.value, self.type_map["float"]
                return ir.Constant(Type, value), Type
            case NodeType.IdentifierLiteral:
                node: IdentifierLiteral = node
                ptr, Type = self.env.lookup(node.value)
                return self.builder.load(ptr), Type

            case NodeType.InfixExpression:
                return self.__visit_infix_expression(node)
            case NodeType.CallExpression:
                return self.__visit_call_expression(node)


    def get_function_return_type(self, function_name: str) -> str:
        """Get the return type of function"""
        if function_name in self.module.globals:
            func = self.module.globals[function_name]
            if isinstance(func, ir.Function):
                return_type = func.function_type.return_type
                if isinstance(return_type, ir.IntType):
                    return "int"
                elif isinstance(return_type, ir.FloatType):
                    return "float"
                elif isinstance(return_type, ir.IntType) and return_type.width == 1:
                    return "bool"
                elif isinstance(return_type, (ir.PointerType, ir.ArrayType)):
                    return "str"
        return "unknown"
