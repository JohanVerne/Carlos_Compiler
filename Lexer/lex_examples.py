import os
import sys

# Add the parent directory to the sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
sys.path.append(parent_dir)

from Lexer.lexer import Lexer


# Lex every file in the examples directory to test the lexer on basic examples
# We can create comments lexems since we parse line by line
class LexExemples:
    def lex_files_in_directory(self, directory):
        output_directory = os.path.join(directory, "../Lexer/examples_lexed")
        os.makedirs(output_directory, exist_ok=True)
        for filename in os.listdir(directory):
            if filename.endswith(".carlos"):
                filepath = os.path.join(directory, filename)
                with open(filepath, "r") as file:
                    content = file.readlines()
                    lexer = Lexer()  # Instantiate a new Lexer for each file
                    lexems = lexer.lex(content)
                    output_filepath = os.path.join(
                        output_directory, filename + "_lexed.txt"
                    )
                    self.save_lexems_to_file(lexems, output_filepath)

    def save_lexems_to_file(self, lexems, output_filepath):
        with open(output_filepath, "w") as file:
            for lexem in lexems:
                file.write(f"{lexem.tag}: {lexem.value} at {lexem.position}\n")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    examples_directory = os.path.join(script_dir, "../examples")
    LexExemples().lex_files_in_directory(examples_directory)
