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


# Parse every file in the examples directory after having lexed them to test the lexer on basic examples
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
        with open(output_filepath, "w") as file:
            file.write(self.format_ast(ast))

    def format_ast(self, node, indent=0):
        """
        Recursively format the AST for better readability with consistent indentation.
        """
        if isinstance(node, list):
            return "\n".join(self.format_ast(child, indent) for child in node)
        elif isinstance(node, dict):
            result = ""
            for key, value in node.items():
                result += f"{'  ' * indent}{key}:\n"
                result += self.format_ast(value, indent + 1)
            return result
        elif isinstance(node, ASTNode):
            result = "  " * indent + f"{node.__class__.__name__}\n"
            for attr, value in vars(node).items():
                result += f"{'  ' * (indent + 1)}{attr}:\n"
                result += self.format_ast(value, indent + 2)
            return result
        else:
            return "  " * indent + repr(node) + "\n"


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    examples_directory = os.path.join(script_dir, "../examples")
    ParseExamples().parse_files_in_directory(examples_directory)
