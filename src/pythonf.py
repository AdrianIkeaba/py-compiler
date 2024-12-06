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

# Constants representing different data types
TYPE_INT = 0
TYPE_FLOAT = 1
TYPE_CHAR = 2
TYPE_BOOL = 3
TYPE_STRING = 4

class ReturnValue(Structure):
    """Structure to hold the return value from the compiled function."""
    _fields_ = [
        ("type", c_int),  # Type of the return value
        ("value", POINTER(c_char))  # Pointer to the value
    ]

def get_return_value(result: ReturnValue):
    """Convert the return value to the appropriate Python type."""
    if result.type == TYPE_INT:
        return int.from_bytes(result.value.contents.value, byteorder='little')  # Convert bytes to int
    elif result.type == TYPE_FLOAT:
        return struct.unpack('f', result.value.contents.value)[0]  # Unpack bytes to float
    elif result.type == TYPE_BOOL:
        return bool(int.from_bytes(result.value.contents.value, byteorder='little'))  # Convert bytes to bool
    elif result.type == TYPE_STRING:
        return result.value.decode('utf-8')  # Decode bytes to string
    elif result.type == TYPE_CHAR:
        return chr(result.value.contents.value[0])  # Convert bytes to char
    else:
        return f"Unknown type: {result.type}"  # Handle unknown type

def compile_and_run(file_path):
    """Compile and run the source code from the given file path."""
    # Read the source code
    try:
        with open(file_path, "r") as f:
            code = f.read()  # Read the entire file content
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")  # Handle file not found error
        sys.exit(1)
    except IOError:
        print(f"Error: Could not read file '{file_path}'.")  # Handle IO error
        sys.exit(1)

    l = Lexer(source=code)  # Initialize the lexer with the source code
    p = Parser(l)  # Initialize the parser with the lexer

    # Parse the program
    program = p.parse_program()  # Parse the source code into an AST
    if len(p.errors) > 0:
        for err in p.errors:
            print(err)  # Print any parsing errors
        sys.exit(1)

    # Compile the parsed program
    c = Compiler()  # Create a compiler instance
    c.compile(program)  # Compile the AST

    module = ir.Module = c.module  # Get the LLVM module from the compiler
    module.triple = llvm.get_default_triple()  # Set the target triple for the module

    # Initialize LLVM
    llvm.initialize()  # Initialize LLVM
    llvm.initialize_native_target()  # Initialize the native target
    llvm.initialize_native_asmparser()  # Initialize the native assembly parser
    llvm.initialize_native_asmprinter()  # Initialize the native assembly printer

    # Parse and verify LLVM IR
    try:
        llvm_ir_parsed = llvm.parse_assembly(str(module))  # Parse the LLVM IR
        llvm_ir_parsed.verify()  # Verify the parsed LLVM IR
    except Exception as e:
        print(f"LLVM IR Verification Error: {e}")  # Handle verification errors
        sys.exit(1)

    # Create execution engine
    target_machine = llvm.Target.from_default_triple().create_target_machine()  # Create target machine
    engine = llvm.create_mcjit_compiler(llvm_ir_parsed, target_machine)  # Create the JIT compiler
    engine.finalize_object()  # Finalize the object for execution

    # Get and run main function
    entry = engine.get_function_address('main')  # Get the address of the 'main' function

    # Determine return type based on function signature
    return_type = c.get_function_return_type('main')  # Get the return type of the 'main' function

    # Select appropriate C function type based on the return type
    if return_type == "int":
        cfunc = CFUNCTYPE(c_int)(entry)  # Define C function type for int return
    elif return_type == "float":
        cfunc = CFUNCTYPE(c_float)(entry)  # Define C function type for float return
    elif return_type == "bool":
        cfunc = CFUNCTYPE(c_bool)(entry)
    elif return_type == "str":
        cfunc = CFUNCTYPE(c_char_p)(entry)  # Define C function type for string return
    else:
        cfunc = CFUNCTYPE(None)(entry) # Define C function, can handle print statetements or void functions

    # Execute and time the function
    st = time.time()  # Start timing the execution
    result = cfunc()  # Call the compiled function
    et = time.time()  # End timing the execution

    # Format and display the result based on the return type
    if return_type == "str":
        if result:
            print(result.decode("utf-8"))  # Print the returned string
        else:
            print("Null string returned")  # Handle null string return
    else:
        print(result)  # Print the result for other types

    print(f'Executed in {round((et - st) * 1000, 3)}ms')  # Print the execution time in milliseconds

def main():
    """Main function to handle command line arguments and initiate compilation and execution."""
    # Check if a file path is provided
    if len(sys.argv) != 2:
        print("Usage: pythonf <file_path>.py")  # Print usage instructions
        sys.exit(1)  # Exit if the usage is incorrect

    # Get the file path from command line arguments
    file_path = sys.argv[1]

    # Compile and run the file
    compile_and_run(file_path)  # Call the compile and run function with the provided file path

if __name__ == '__main__':
    main()  # Execute the main function when the script is run