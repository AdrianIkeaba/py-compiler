from Lexer import Lexer
from Parser import Parser
from Compiler import Compiler
from AST import Program
import json
import time
import struct

from llvmlite import ir
import llvmlite.binding as llvm
from ctypes import CFUNCTYPE, Structure, c_int, c_float, c_char, c_bool, POINTER, c_char_p

LEXER_DEBUG: bool = False
PARSER_DEBUG: bool = True
COMPILER_DEBUG: bool = False
RUN_CODE: bool = False

# Define return type constants
TYPE_INT = 0
TYPE_FLOAT = 1
TYPE_CHAR = 2
TYPE_BOOL = 3
TYPE_STRING = 4


class ReturnValue(Structure):
    _fields_ = [
        ("type", c_int),
        ("value", POINTER(c_char))  # Universal pointer to hold any type
    ]


def get_return_value(result: ReturnValue):
    """Convert the return value to the appropriate Python type"""
    if result.type == TYPE_INT:
        return int.from_bytes(result.value.contents.value, byteorder='little')
    elif result.type == TYPE_FLOAT:
        # Use struct to unpack bytes into float
        return struct.unpack('f', result.value.contents.value)[0]
    elif result.type == TYPE_BOOL:
        return bool(int.from_bytes(result.value.contents.value, byteorder='little'))
    elif result.type == TYPE_STRING:
        return result.value.decode('utf-8')
    elif result.type == TYPE_CHAR:
        return chr(result.value.contents.value[0])
    else:
        return f"Unknown type: {result.type}"


if __name__ == '__main__':
    # Read source code
    with open("tests/test.py", "r") as f:
        code: str = f.read()

    # Lexer debug
    if LEXER_DEBUG:
        print("===== LEXER DEBUG =====")
        debug_lex: Lexer = Lexer(source=code)
        while debug_lex.current_char is not None:
            print(debug_lex.next_token())

    # Parse code
    l: Lexer = Lexer(source=code)
    p: Parser = Parser(l)

    program: Program = p.parse_program()
    if len(p.errors) > 0:
        for err in p.errors:
            print(err)
        exit(1)

    # Parser debug
    if PARSER_DEBUG:
        print("===== PARSER_DEBUG =====")
        with open("debug/ast.json", "w") as f:
            json.dump(program.json(), f, indent=4)
        print("Wrote AST to debug/ast.json successfully")

    # Compile code
    c: Compiler = Compiler()
    c.compile(node=program)

    # Output steps
    module: ir.Module = c.module
    module.triple = llvm.get_default_triple()

    # Compiler debug
    if COMPILER_DEBUG:
        with open("debug/ir.ll", "w") as f:
            f.write(str(module))

    # Run code
    if RUN_CODE:
        # Initialize LLVM
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmparser()
        llvm.initialize_native_asmprinter()

        # Parse and verify LLVM IR
        try:
            llvm_ir_parsed = llvm.parse_assembly(str(module))
            llvm_ir_parsed.verify()
        except Exception as e:
            print(e)
            raise

        # Create execution engine
        target_machine = llvm.Target.from_default_triple().create_target_machine()
        engine = llvm.create_mcjit_compiler(llvm_ir_parsed, target_machine)
        engine.finalize_object()

        # Get and run main function
        entry = engine.get_function_address('main')

        # Determine return type based on function signature
        return_type = c.get_function_return_type('main')

        if return_type == "int":
            cfunc = CFUNCTYPE(c_int)(entry)
        elif return_type == "float":
            cfunc = CFUNCTYPE(c_float)(entry)
        elif return_type == "bool":
            cfunc = CFUNCTYPE(c_bool)(entry)
        elif return_type == "str":
            cfunc = CFUNCTYPE(c_char_p)(entry)
        else:
            raise ValueError(f"Unsupported return type: {return_type}")

        # Execute and time the function
        st = time.time()
        result = cfunc()
        et = time.time()

        # Format and display the result based on the return type
        if return_type == "str":
            if result:
                print(f'\n{result.decode("utf-8")}')
            else:
                print("\nNull string returned")
        else:
            print(f'\n{result}')

        print(f'==== Executed in {round((et - st) * 1000, 3)}ms ====\n')