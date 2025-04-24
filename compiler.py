import os
import sys
import subprocess

# Add the parent directory and the Parser directory to the sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
sys.path.append(parent_dir)
sys.path.append(os.path.join(parent_dir, "Parser"))  # Add Parser directory to path

from Lexer.lexer import Lexer
from Parser.parser import Parser
from Parser.AST import *  # Ensure AST is imported correctly
from Visitors.JSCodeGenerator import JSCodeGenerator


class Compiler:
    """
    Main compiler class that takes a .carlos file, compiles it, and executes it as JavaScript.
    """

    def __init__(self):
        # Update the output directory to Visitors/examples_js
        self.output_directory = os.path.join(script_dir, "Visitors/examples_js")
        os.makedirs(self.output_directory, exist_ok=True)

    def compile(self, input_filepath, save_js=True):
        """
        Compile the given .carlos file into JavaScript and execute it.
        :param input_filepath: Path to the input .carlos file.
        :param save_js: Boolean indicating whether to save the generated .js file.
        """
        if not input_filepath.endswith(".carlos"):
            raise ValueError("Input file must have a .carlos extension")

        # Step 1: Read the input file
        with open(input_filepath, "r") as file:
            content = file.readlines()

        # Step 2: Lexing
        lexer = Lexer()
        lexems = lexer.lex(content)

        # Step 3: Parsing
        parser = Parser(lexems)
        ast = parser.parse()

        # Step 4: JavaScript Code Generation
        generator = JSCodeGenerator()
        js_code = ast.accept(generator)

        if save_js:
            # Step 5: Save the generated JavaScript code to a file
            output_filename = os.path.basename(input_filepath).replace(".carlos", ".js")
            output_filepath = os.path.join(self.output_directory, output_filename)
            with open(output_filepath, "w") as file:
                file.write(js_code)

            print(f"JavaScript file generated: {output_filepath}")
        else:
            print("JavaScript file generation skipped.")

        # Step 6: Execute the JavaScript code
        self.execute_js(
            js_code if not save_js else output_filepath, is_code=not save_js
        )

    def execute_js(self, js_code_or_filepath, is_code=False):
        """
        Execute the generated JavaScript code or file using Node.js.
        :param js_code_or_filepath: JavaScript code as a string or the path to the .js file.
        :param is_code: Boolean indicating whether the input is raw JavaScript code.
        """
        try:
            if is_code:
                result = subprocess.run(
                    ["node", "-e", js_code_or_filepath],
                    capture_output=True,
                    text=True,
                    check=True,
                )
            else:
                result = subprocess.run(
                    ["node", js_code_or_filepath],
                    capture_output=True,
                    text=True,
                    check=True,
                )
            print("Execution Output:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error during execution:")
            print(e.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 compiler.py <input_file.carlos> [--save]")
        sys.exit(1)

    input_file = sys.argv[1]
    save_js = "--save" in sys.argv  # Save only if --save is explicitly provided

    compiler = Compiler()
    compiler.compile(input_file, save_js=save_js)
