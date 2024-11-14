#!/usr/bin/env python3
import sys
import struct
import time

from llvmlite import ir
import llvmlite.binding as llvm
from ctypes import CFUNCTYPE, c_int, c_float, c_char, c_bool, c_char_p
from _ctypes import Structure, POINTER

from Lexer import Lexer
from Parser import Parser
from Compiler import Compiler

TYPE_INT = 0
TYPE_FLOAT = 1
TYPE_CHAR = 2
TYPE_BOOL = 3
TYPE_STRING = 4

class ReturnValue(Structure):
    _fields_ = [
        ("type", c_int),
        ("value", POINTER(c_char))
    ]

def get_return_value(result: ReturnValue):
    """Convert the return value to the appropriate Python type"""
    if result.type == TYPE_INT:
        return int.from_bytes(result.value.contents.value, byteorder='little')
    elif result.type == TYPE_FLOAT:
        return struct.unpack('f', result.value.contents.value)[0]
    elif result.type == TYPE_BOOL:
        return bool(int.from_bytes(result.value.contents.value, byteorder='little'))
    elif result.type == TYPE_STRING:
        return result.value.decode('utf-8')
    elif result.type == TYPE_CHAR:
        return chr(result.value.contents.value[0])
    else:
        return f"Unknown type: {result.type}"

def compile_and_run(file_path):
    # Read the source code
    try:
        with open(file_path, "r") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except IOError:
        print(f"Error: Could not read file '{file_path}'.")
        sys.exit(1)

    l = Lexer(source=code)
    p = Parser(l)

    # Parse the program
    program = p.parse_program()
    if len(p.errors) > 0:
        for err in p.errors:
            print(err)
        sys.exit(1)

    # Compile
    c = Compiler()
    c.compile(program)

    module = ir.Module = c.module
    module.triple = llvm.get_default_triple()

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
        print(f"LLVM IR Verification Error: {e}")
        sys.exit(1)

    # Create execution engine
    target_machine = llvm.Target.from_default_triple().create_target_machine()
    engine = llvm.create_mcjit_compiler(llvm_ir_parsed, target_machine)
    engine.finalize_object()

    # Get and run main function
    entry = engine.get_function_address('main')

    # Determine return type based on function signature
    return_type = c.get_function_return_type('main')

    # Select appropriate C function type
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
            print(result.decode("utf-8"))
        else:
            print("Null string returned")
    else:
        print(result)

    print(f'Executed in {round((et - st) * 1000, 3)}ms')

def main():
    # Check if a file path is provided
    if len(sys.argv) != 2:
        print("Usage: pythonf <file_path>.py")
        sys.exit(1)

    # Get the file path
    file_path = sys.argv[1]

    # Compile and run the file
    compile_and_run(file_path)

if __name__ == '__main__':
    main()