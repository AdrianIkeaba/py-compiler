from setuptools import setup, find_packages

# Setup configuration for the Python package
setup(
    name='pythonf',  # Name of the package
    version='0.1.0',  # Version of the package
    packages=find_packages(),  # Automatically find and include all packages in the project
    install_requires=[
        'llvmlite',  # Dependency for LLVM bindings
        # Add other dependencies from your project
    ],
    entry_points={
        'console_scripts': [
            'pythonf=pythonf:main',  # Entry point for the command line interface
        ],
    },
    author='Your Name',  # Author of the package
    description='A custom Python-like compiler',  # Brief description of the package
)