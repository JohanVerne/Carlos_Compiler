import os
import sys

# Add the parent directory to the sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
sys.path.append(parent_dir)
sys.path.append(os.path.join(parent_dir, "Parser"))  # Add Parser directory to path


from Lexer.lexer import Lexer
from Parser.parser import Parser
from Visitors.PrettyPrinter import PrettyPrinter


# Pretty-prints all `.carlos` files in the examples directory after parsing them into an AST.
# The output is saved in a separate directory.
class PrettyPrintExamples:
    def pretty_print_files_in_directory(self, directory):
        output_directory = os.path.join(directory, "../Visitors/examples_prettyprinted")
        os.makedirs(output_directory, exist_ok=True)
        for filename in os.listdir(directory):
            if filename.endswith(".carlos"):
                filepath = os.path.join(directory, filename)
                with open(filepath, "r") as file:
                    content = file.readlines()
                    lexer = Lexer()
                    lexems = lexer.lex(content)
                    parser = Parser(lexems)
                    ast = parser.parse()
                    output_filepath = os.path.join(
                        output_directory, filename.replace(".carlos", "_pretty.carlos")
                    )
                    self.save_pretty_print_to_file(ast, output_filepath)

    def save_pretty_print_to_file(self, ast, output_filepath):
        """
        Save the pretty-printed source code to a file.
        """
        printer = PrettyPrinter()
        with open(output_filepath, "w") as file:
            output = ast.accept(printer)  # Pretty-print the AST
            file.write(output)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    examples_directory = os.path.join(script_dir, "../examples")
    PrettyPrintExamples().pretty_print_files_in_directory(examples_directory)
