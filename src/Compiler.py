from llvmlite import ir  # Import LLVM IR types and functionalities

# Import necessary node types and expressions from the Abstract Syntax Tree (AST) module
from AST import NodeType, Expression, Program, Node
from AST import ExpressionStatement, VariableStatement, IdentifierLiteral, BlockStatement, FunctionStatement, ReturnStatement, AssignStatement
from AST import InfixExpression, CallExpression
from AST import IntegerLiteral, FloatLiteral

from Environment import Environment  # Import the Environment class for symbol table management

class Compiler:
    """Compiler class responsible for compiling the AST into LLVM IR."""

    def __init__(self) -> None:
        """Initialize the compiler with necessary components."""
        # Mapping of high-level types to LLVM IR types
        self.type_map: dict[str, ir.Type] = {
            'int': ir.IntType(32),  # 32-bit integer type
            'float': ir.FloatType(),  # Floating-point type
        }

        # Create an LLVM module named 'main' to hold the compiled code
        self.module: ir.Module = ir.Module('main')

        # Create an LLVM IR builder for constructing the IR
        self.builder: ir.IRBuilder = ir.IRBuilder()

        # Initialize the environment (symbol table) for variable management
        self.env: Environment = Environment()

        # List to store compilation errors
        self.errors: list[str] = []

    def compile(self, node: Node) -> None:
        """Compile the given AST node based on its type."""
        match node.type():  # Match the type of the node
            case NodeType.Program:
                self.__visit_program(node)  # Visit program node

            case NodeType.VariableStatement:
                self.__visit_variable_statement(node)  # Visit variable declaration
            case NodeType.ExpressionStatement:
                self.__visit_expression_statement(node)  # Visit expression statement
            case NodeType.BlockStatement:
                self.__visit_block_statement(node)  # Visit block statement
            case NodeType.FunctionStatement:
                self.__visit_function_statement(node)  # Visit function declaration
            case NodeType.ReturnStatement:
                self.__visit_return_statement(node)  # Visit return statement
            case NodeType.AssignStatement:
                self.__visit_assign_statement(node)  # Visit assignment statement

            case NodeType.InfixExpression:
                self.__visit_infix_expression(node)  # Visit infix expression
            case NodeType.CallExpression:
                self.__visit_call_expression(node)  # Visit function call expression

    def __visit_program(self, node: Program) -> None:
        """Visit a program node and compile its statements."""
        for stmt in node.statements:  # Iterate through each statement in the program
            self.compile(stmt)  # Compile each statement

    def __visit_expression_statement(self, node: ExpressionStatement) -> None:
        """Visit an expression statement node."""
        self.compile(node.expr)  # Compile the expression contained in the statement

    def __visit_variable_statement(self, node: VariableStatement) -> None:
        """Visit a variable declaration statement node."""
        name: str = node.name.value  # Get the variable name
        value: Expression = node.value  # Get the assigned value
        value_type: str = node.value_type  # Get the type of the variable (e.g., int, float)

        # Resolve the value to its LLVM representation
        value, Type = self.__resolve_value(value)

        # Check if the variable is already declared in the environment
        if self.env.lookup(name) is None:
            # If not declared, get the corresponding LLVM type
            llvm_type = self.type_map.get(value_type, None)
            if llvm_type is None:
                # If the type is unknown, log an error
                self.errors.append(f"Unknown type '{value_type}' for variable '{name}'.")
                return

            # Allocate space for the variable in the LLVM IR
            ptr = self.builder.alloca(llvm_type, name=name)

            # Store the value in the allocated space
            self.builder.store(value, ptr)

            # Define the variable in the environment with its pointer and type
            self.env.define(name, ptr, Type)
        else:
            # If the variable is already declared, retrieve its pointer
            ptr, _ = self.env.lookup(name)
            # Update the value at the pointer
            self.builder.store(value, ptr)

    def __visit_block_statement(self, node: BlockStatement) -> None:
        """Visit a block statement node."""
        for stmt in node.statements:  # Iterate through each statement in the block
            self.compile(stmt)  # Compile each statement

    def __visit_return_statement(self, node: ReturnStatement) -> None:
        """Visit a return statement node."""
        value: Expression = node.return_value  # Get the return value expression
        value, Type = self.__resolve_value(value)  # Resolve the return value to its LLVM representation

        self.builder.ret(value)  # Generate the LLVM IR for returning the value

    def __visit_function_statement(self, node: FunctionStatement) -> None:
        """Visit a function declaration statement node."""
        name: str = node.name.value  # Get the function name
        body: BlockStatement = node.body  # Get the function body as a block statement
        params: list[IdentifierLiteral] = node.parameters  # Get the function parameters

        # Extract parameter names for later use
        param_names: list[str] = [p.value.name for p in params]

        param_types: list[ir.Type] = []  # TODO: Define parameter types based on the function signature

        # Get the return type of the function from the type map
        return_type: ir.Type = self.type_map[node.return_type]

        # Create the function type for LLVM
        fnty: ir.FunctionType = ir.FunctionType(return_type, param_types)
        # Create the function in the LLVM module
        func: ir.Function = ir.Function(self.module, fnty, name)

        # Create a new basic block for the function entry
        block = func.append_basic_block(f"{name}_entry")

        # Save the current IR builder and switch to the new block
        previous_builder = self.builder
        self.builder = ir.IRBuilder(block)

        # Save the current environment and create a new one for the function scope
        previous_env = self.env
        self.env = Environment(parent=self.env)  # Create a new environment with the current one as parent
        self.env.define(name, func, return_type)  # Define the function in the environment

        # Compile the function body
        self.compile(body)

        # Restore the previous environment and define the function again
        self.env = previous_env
        self.env.define(name, func, return_type)

        # Restore the previous IR builder
        self.builder = previous_builder

    def __visit_assign_statement(self, node: AssignStatement) -> None:
        """Visit an assignment statement node."""
        name: str = node.identifier.value  # Get the variable name being assigned to
        value: Expression = node.right_value  # Get the value being assigned

        # Resolve the value to its LLVM representation
        value, Type = self.__resolve_value(value)

        # Check if the variable is declared in the environment
        if self.env.lookup(name) is None:
            # Log an error if the variable has not been declared
            self.errors.append(f"Compile Error: {name} has not been declared.")
        else:
            # If declared, retrieve the variable's pointer
            ptr, _ = self.env.lookup(name)
            # Store the new value at the variable's pointer
            self.builder.store(value, ptr)

    def __visit_infix_expression(self, node: InfixExpression) -> None:
        """Visit an infix expression node (e.g., a + b)."""
        operator: str = node.operator  # Get the operator (e.g., +, -, *, /)
        # Resolve the left and right operands to their LLVM representations
        left_value, left_type = self.__resolve_value(node.left_node)
        right_value, right_type = self.__resolve_value(node.right_node)

        value = None  # Variable to hold the result of the operation
        Type = None  # Variable to hold the type of the result

        # Check if both operands are integers
        if isinstance(right_type, ir.IntType) and isinstance(left_type, ir.IntType):
            Type = self.type_map["int"]  # Set the result type to int
            match operator:  # Match the operator to generate the appropriate LLVM IR
                case '+':
                    value = self.builder.add(left_value, right_value)  # Generate addition
                case '-':
                    value = self.builder.sub(left_value, right_value)  # Generate subtraction
                case '*':
                    value = self.builder.mul(left_value, right_value)  # Generate multiplication
                case '/':
                    value = self.builder.sdiv(left_value, right_value)  # Generate integer division
                case '%':
                    value = self.builder.srem(left_value, right_value)  # Generate modulus
                case '**':
                    # TODO: Handle exponentiation
                    pass
        # Check if both operands are floats
        elif isinstance(right_type, ir.FloatType) and isinstance(left_type, ir.FloatType):
            Type = ir.FloatType()  # Set the result type to float
            match operator:  # Match the operator to generate the appropriate LLVM IR
                case '+':
                    value = self.builder.fadd(left_value, right_value)  # Generate addition
                case '-':
                    value = self.builder.fsub(left_value, right_value)  # Generate subtraction
                case '*':
                    value = self.builder.fmul(left_value, right_value)  # Generate multiplication
                case '/':
                    value = self.builder.fdiv(left_value, right_value)  # Generate floating-point division
                case '%':
                    # TODO: Handle modulus for floats
                    pass
                case '**':
                    # TODO: Handle exponentiation for floats
                    pass

        return value, Type  # Return the result and its type

    def __visit_call_expression(self, node: CallExpression) -> None:
        """Visit a function call expression node."""
        name: str = node.function.value  # Get the function name
        params: list[Expression] = node.arguments  # Get the function arguments

        args = []  # List to store LLVM IR values of the arguments
        types = []  # List to store LLVM IR types of the arguments

        # Resolve each argument to its LLVM representation
        for param in params:
            value, Type = self.__resolve_value(param)
            args.append(value)
            types.append(Type)

        # Look up the function in the environment
        func, ret_type = self.env.lookup(name)

        # Generate the function call with the LLVM IR values of the arguments
        ret = self.builder.call(func, args)

        return ret, ret_type

    def __resolve_value(self, node: Expression) -> tuple[ir.Value, ir.Type]:
        """Resolve an expression to its LLVM IR value and type."""
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
        """Get the return type of a function."""
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