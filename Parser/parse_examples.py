import os
import sys

# Add the parent directory to the sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
sys.path.append(parent_dir)

from Lexer.lexer import Lexer
from parser import Parser
from Lexer.lex_examples import LexExemples
from AST import ASTNode
from Visitors.ASTPrinter import ASTPrinter


# Parse every file in the examples directory after having lexed them to test the parser on basic examples
class ParseExamples:
    def parse_files_in_directory(self, directory):
        output_directory = os.path.join(directory, "../Parser/examples_parsed")
        os.makedirs(output_directory, exist_ok=True)
        for filename in os.listdir(directory):
            if filename.endswith(".carlos"):
                filepath = os.path.join(directory, filename)
                with open(filepath, "r") as file:
                    content = file.readlines()
                    lexer = Lexer()  # Instantiate a new Lexer for each file
                    lexems = lexer.lex(content)
                    parser = Parser(lexems)  # Instantiate a new Parser for each file
                    ast = parser.parse()  # Parse and generate the AST
                    output_filepath = os.path.join(
                        output_directory, filename + "_ast.txt"
                    )
                    self.save_ast_to_file(ast, output_filepath)

    def save_ast_to_file(self, ast, output_filepath):
        """
        Save the generated AST to a file for debugging purposes.
        """
        printer = ASTPrinter()
        with open(output_filepath, "w") as file:
            output = ast.accept(printer)  # Print the AST(ast)
            file.write(output)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    examples_directory = os.path.join(script_dir, "../examples")
    ParseExamples().parse_files_in_directory(examples_directory)
