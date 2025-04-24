import os
import sys

# Add the parent directory and the Parser directory to the sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
sys.path.append(parent_dir)
sys.path.append(os.path.join(parent_dir, "Parser"))  # Add Parser directory to path

from Lexer.lexer import Lexer
from Parser.parser import Parser
from Visitors.JSCodeGenerator import JSCodeGenerator


class CreateJSFilesFromExamples:
    """
    Generates JavaScript files from `.carlos` files in the examples directory
    by parsing them into an AST and converting them using JSCodeGenerator.
    The output is saved in a separate directory.
    """

    def generate_js_files_in_directory(self, directory):
        output_directory = os.path.join(directory, "../Visitors/examples_js")
        os.makedirs(output_directory, exist_ok=True)

        for filename in os.listdir(directory):
            if filename.endswith(".carlos"):
                filepath = os.path.join(directory, filename)
                with open(filepath, "r") as file:
                    content = file.readlines()

                    # Lexing
                    lexer = Lexer()
                    lexems = lexer.lex(content)

                    # Parsing
                    parser = Parser(lexems)
                    ast = parser.parse()

                    # JavaScript code generation
                    output_filepath = os.path.join(
                        output_directory, filename.replace(".carlos", ".js")
                    )
                    self.save_js_to_file(ast, output_filepath)

    def save_js_to_file(self, ast, output_filepath):
        """
        Save the generated JavaScript code to a file.
        """
        generator = JSCodeGenerator()
        with open(output_filepath, "w") as file:
            output = ast.accept(generator)  # Generate JavaScript code from the AST
            file.write(output)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    examples_directory = os.path.join(script_dir, "../examples")
    CreateJSFilesFromExamples().generate_js_files_in_directory(examples_directory)
