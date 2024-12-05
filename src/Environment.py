# This class serves as the symbol table for the compiler, managing variable definitions and scopes - Gara 
from llvmlite import ir  # Import LLVM IR types for value and type representation

class Environment:
    def __init__(self, records: dict[str, tuple[ir.Value, ir.Type]] = None, parent = None, name: str = "global") -> None:
        """
        Initialize the Environment with an optional set of records, a parent environment, and a name.
        
        Args:
            records (dict[str, tuple[ir.Value, ir.Type]]): A dictionary mapping variable names to their values and types.
            parent (Environment): The parent environment for nested scopes (e.g., function scopes).
            name (str): The name of this environment, defaulting to "global".
        """
        # If no records are provided, initialize an empty dictionary to hold variable definitions.
        self.records: dict[str, tuple] = records if records else {}
        self.parent = parent  # Set the parent environment for scope resolution.
        self.name: str = name  # Name of the environment, useful for debugging.

    def define(self, name: str, value: ir.Value, _type: ir.Type) -> ir.Value:
        """
        Define a new variable in the current environment.
        
        Args:
            name (str): The name of the variable to define.
            value (ir.Value): The LLVM IR value associated with the variable.
            _type (ir.Type): The LLVM IR type of the variable.
        
        Returns:
            ir.Value: The value that was defined.
        """
        # Store the variable name along with its value and type in the records dictionary.
        self.records[name] = (value, _type)
        return value  # Return the value for convenience.

    def lookup(self, name: str) -> tuple[ir.Value, ir.Type]:
        """
        Look up a variable by name in the current environment and its parent environments.
        
        Args:
            name (str): The name of the variable to look up.
        
        Returns:
            tuple[ir.Value, ir.Type]: The value and type of the variable, or None if not found.
        """
        return self.__resolve(name)  # Delegate the actual resolution to the private __resolve method.

    def __resolve(self, name: str) -> tuple[ir.Value, ir.Type]:
        """
        Resolve a variable name to its value and type, searching through the current and parent environments.
        
        Args:
            name (str): The name of the variable to resolve.
        
        Returns:
            tuple[ir.Value, ir.Type]: The value and type of the variable if found; None otherwise.
        """
        # Check if the variable exists in the current environment's records.
        if name in self.records:
            return self.records[name]  # Return the value and type if found.

        # If not found, check the parent environment (if it exists) for the variable.
        elif self.parent:
            return self.parent.__resolve(name)  # Recursively resolve in the parent environment.

        # If the variable is not found in any environment, return None.
        else:
            return None  # Variable not found; return None to indicate this.