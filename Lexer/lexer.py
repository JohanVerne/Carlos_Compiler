import re
import sys
import os

regex_expressions = [
    # comments
    (r"\/\/.*", "COMMENTS"),
    # function
    (r"function\b", "FUNCTION"),
    # left parentheses
    (r"\(", "LPAREN"),
    # right parentheses
    (r"\)", "RPAREN"),
    # colon
    (r"\:", "COLON"),
    # Inclusive range
    (r"\.\.\.", "INCLUSIVE_RANGE"),
    # Exclusive range
    (r"\.\.<", "EXCLUSIVE_RANGE"),
    # semicolon
    (r"\;", "SEMICOLON"),
    # arrow
    (r"\-\>", "ARROW"),
    # any
    (r"any\b", "ANY"),
    # left braces
    (r"\{", "LBRACE"),
    # right braces
    (r"\}", "RBRACE"),
    # return
    (r"return\b", "RETURN"),
    # slash
    (r"\/", "DIVISION"),
    # print
    (r"print\b", "PRINT"),
    # float literals
    (r"[-]?[0-9]*[.]?[0-9]+?[eE]?[-+]?[0-9]*?", "FLOAT_LITERAL"),
    # int
    (r"int\b", "INT"),
    # integer literals
    (r"[0-9]+", "INTEGER_LITERAL"),
    # float
    (r"float\b", "FLOAT"),
    # increment
    (r"\+\+", "INCREMENT"),
    # decrement
    (r"--", "DECREMENT"),
    # plus
    (r"\+", "PLUS"),
    # minus
    (r"\-", "MINUS"),
    # multiplication
    (r"\*", "MULTIPLICATION"),
    # power
    (r"\*\*", "POWER"),
    # equality
    (r"\=\=", "IS_EQUAL"),
    # equal
    (r"\=", "EQUAL"),
    # is not equal
    (r"\!\=", "IS_NOT_EQUAL"),
    # comma
    (r"\,", "COMMA"),
    # double question mark
    (r"\?\?", "DOUBLE_QUESTION_MARK"),
    # optional member variable
    (r"\?\.", "OPTIONAL_MEMBER"),
    # question mark
    (r"\?", "QUESTION_MARK"),
    # modulo
    (r"\%", "MODULO"),
    # string
    (r"string\b", "STRING"),
    # string literals
    (r'\"(?:\\.|[^"\\])*\"', "STRING_LITERAL"),
    # less than or equal to
    (r"\<\=", "LESS_THAN_EQUAL"),
    # greater than or equal to
    (r"\>\=", "GREATER_THAN_EQUAL"),
    (r"\<\<", "LEFT_SHIFT"),
    # right shift
    (r"\>\>", "RIGHT_SHIFT"),
    # less than
    (r"\<", "LESS_THAN"),
    # greater than
    (r"\>", "GREATER_THAN"),
    # let
    (r"let\b", "LET"),
    # if
    (r"if\b", "IF"),
    # else
    (r"else\b", "ELSE"),
    # const
    (r"const\b", "CONST"),
    # random
    (r"random\b", "RANDOM"),
    # left brackets
    (r"\[", "LBRACKET"),
    # right brackets
    (r"\]", "RBRACKET"),
    # repeat
    (r"repeat\b", "REPEAT"),
    # no
    (r"no\b", "NO"),
    # struct
    (r"struct\b", "STRUCT"),
    # some
    (r"some\b", "SOME"),
    # for
    (r"for\b", "FOR"),
    # in
    (r"in\b", "IN"),
    # boolean
    (r"boolean\b", "BOOLEAN"),
    # true
    (r"true\b", "TRUE"),
    # false
    (r"false\b", "FALSE"),
    # void
    (r"void\b", "VOID"),
    # break
    (r"break\b", "BREAK"),
    # while
    (r"while\b", "WHILE"),
    # dot
    (r"\.", "DOT"),
    # length
    (r"\#", "LENGTH"),
    # bitwise complement
    (r"\~", "BITWISE_COMPLEMENT"),
    # not
    (r"\!", "NOT"),
    # left shift
    # logic or
    (r"\|\|", "LOGICAL_OR"),
    # logic and
    (r"\&\&", "LOGICAL_AND"),
    # bitwise and
    (r"\&", "BITWISE_AND"),
    # bitwise or
    (r"\|", "BITWISE_OR"),
    # bitwise xor
    (r"\^", "BITWISE_XOR"),
    # codepoints
    (r"codepoints\b", "CODEPOINTS"),
    # bytes
    (r"bytes\b", "BYTES"),
    # pi
    (r"\π", "PI"),
    # square root
    (r"sqrt\b", "SQRT"),
    # sinus
    (r"sin\b", "SIN"),
    # cosinus
    (r"cos\b", "COS"),
    # exponenential
    (r"exp\b", "EXP"),
    # natural log
    (r"ln\b", "LN"),
    # hypothenuse
    (r"hypot\b", "HYPOT"),
    # Identifier
    (r"[a-zA-Z_][a-zA-Z0-9_]*", "IDENTIFIER"),
    # # Whitespace
    (r"[ \n\t\']+", None),
]


class Lexer:
    """
    Component in charge of the transformation of raw data to lexems.
    """

    def __init__(self, lexems=None):
        self.lexems = lexems if lexems is not None else []

    def lex(self, inputText):
        """
        Main lexer function:
        Creates a lexem for every detected regular expression
        The lexems are composed of:
            - tag
            - values
            - position
        SEE lexem for more info
        """
        # Crawl through the input file
        for lineNumber, line in enumerate(inputText):
            lineNumber += 1
            position = 0
            # Crawl through the line
            while position < len(line):
                match = None
                for lexemRegex in regex_expressions:
                    pattern, tag = lexemRegex
                    regex = re.compile(pattern)
                    match = regex.match(line, position)
                    if match:
                        data = match.group(0)
                        # This condition is needed to avoid the creation of whitespace lexems
                        if tag:
                            lexem = Lexem(tag, data, [lineNumber, position])
                            self.lexems.append(lexem)
                        # Renew the position
                        position = match.end(0)
                        break
                # No match detected --> Wrong syntax in the input file
                if not match:
                    print("No match detected on line and position:")
                    print(line[position:])
                    sys.exit(1)
        # Append EOF token
        self.lexems.append(Lexem("EOF", "", [lineNumber + 1, 0]))
        return self.lexems


class Lexem:
    """
    Our token definition:
    lexem (tag and value) + position in the program raw text
    Parameters
    ----------
    tag: string
        Name of the lexem's type, e.g. IDENTIFIER
    value: string
        Value of the lexem,       e.g. integer1
    position: integer tuple
        Tuple to point out the lexem in the input file (line number, position)
    """

    def __init__(self, tag=None, value=None, position=None):
        self.tag = tag
        self.value = value
        self.position = position

    def __repr__(self):
        return f"{self.tag}({self.value})"


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 lexer.py <input_file> [--save]")
        sys.exit(1)

    input_file = sys.argv[1]
    save_output = "--save" in sys.argv  # Save only if --save is explicitly provided

    # Read the input file
    try:
        with open(input_file, "r") as file:
            input_text = file.readlines()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)

    # Initialize the lexer and process the input
    lexer = Lexer()
    lexems = lexer.lex(input_text)

    # Print the lexems to the terminal
    print("Lexems:")
    for lexem in lexems:
        print(lexem)

    # Save the lexems to a file if --save is provided
    if save_output:
        # Ensure the examples_lexed directory exists
        output_dir = os.path.join(
            os.path.dirname(input_file), "../Lexer/examples_lexed"
        )
        os.makedirs(output_dir, exist_ok=True)

        # Save the lexems in the examples_lexed directory
        output_file = os.path.join(
            output_dir, os.path.basename(input_file) + "_lexed.txt"
        )
        with open(output_file, "w") as file:
            for lexem in lexems:
                file.write(f"{lexem.tag}: {lexem.value} at {lexem.position}\n")
        print(f"Lexems saved to: {output_file}")
