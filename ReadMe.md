### Comments on Important Modules

### `setup.py`
- **Purpose**: Configures the package for distribution.
- **Key Components**:
  - `name`: Specifies the package name.
  - `version`: Indicates the current version of the package.
  - `packages`: Automatically finds and includes all packages.
  - `install_requires`: Lists dependencies required for the package.
  - `entry_points`: Defines command-line interface entry points.

### `src/Lexer.py`
- **Purpose**: Tokenizes the source code into manageable tokens.
- **Key Components**:
  - `__init__`: Initializes the lexer with the source code and sets up initial positions.
  - `__read_char`: Reads the next character from the source.
  - `next_token`: Returns the next token, handling various token types (operators, identifiers, numbers).
  - `__skip_whitespace`: Skips over whitespace characters to avoid unnecessary tokens.
  - `__read_number` and `__read_identifier`: Handle reading numbers and identifiers respectively.

### `src/AST.py`
- **Purpose**: Defines the structure of the abstract syntax tree (AST) for the compiler.
- **Key Components**:
  - `Node`: Base class for all AST nodes.
  - `Program`: Represents the entire program as a collection of statements.
  - `ExpressionStatement`, `IntegerLiteral`, `PrefixExpression`, `InfixExpression`: Various node types representing different constructs in the source code.

### `src/Compiler.py`
- **Purpose**: Compiles the AST into LLVM Intermediate Representation (IR).
- **Key Components**:
  - `__init__`: Initializes the compiler with a new LLVM module and an IR builder.
  - `compile`: Iterates through the program's statements and compiles each one.
  - `compile_statement` and `compile_expression`: Handle the compilation of statements and expressions, respectively, generating the corresponding LLVM IR.

### `src/Environment.py`
- **Purpose**: Manages variable storage and scope for the compiler.
- **Key Components**:
  - `__init__`: Initializes the environment with a store for variables and an optional outer environment.
  - `set`: Stores a variable in the current environment.
  - `get`: Retrieves a variable, checking the current and outer environments.
  - `define`: Defines a new variable in the current environment.

### `src/pythonf.py`
- **Purpose**: Main entry point for the compiler, handling command-line execution.
- **Key Components**:
  - `main`: Reads source code from a file, initializes the lexer and parser, and compiles the resulting AST.
  - Command-line argument handling to specify the source file for compilation.