from setuptools import setup, find_packages

setup(
    name='pythonf',
    version='0.1.0',
    packages=find_packages(),  # This will find the 'compiler' package
    install_requires=[
        'llvmlite',
        # Add other dependencies from your project
    ],
    entry_points={
        'console_scripts': [
            'pythonf=pythonf:main',
        ],
    },
    author='Your Name',
    description='A custom Python-like compiler',
)