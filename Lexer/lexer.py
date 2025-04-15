import re
import sys

regex_expressions = [
    # comments
    (r"\/\/.*", "COMMENTS"),
    # function
    (r"function", "FUNCTION"),
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
    (r"any", "ANY"),
    # left braces
    (r"\{", "LBRACE"),
    # right braces
    (r"\}", "RBRACE"),
    # return
    (r"return", "RETURN"),
    # slash
    (r"\/", "DIVISION"),
    # print
    (r"print", "PRINT"),
    # float literals
    (r"[-]?[0-9]*[.]?[0-9]+?[eE]?[-+]?[0-9]*?", "FLOAT_LITERAL"),
    # int
    (r"int", "INT"),
    # integer literals
    (r"[0-9]+", "INTEGER_LITERAL"),
    # float
    (r"float", "FLOAT"),
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
    (r"string", "STRING"),
    # string literals
    (r'\"(?:\\.|[^"\\])*\"', "STRING_LITERAL"),
    # let
    (r"let", "LET"),
    # less than
    (r"\<", "LESS_THAN"),
    # greater than
    (r"\>", "GREATER_THAN"),
    # less than or equal to
    (r"\<\=", "LESS_THAN_EQUAL"),
    # greater than or equal to
    (r"\>\=", "GREATER_THAN_EQUAL"),
    # if
    (r"if", "IF"),
    # else
    (r"else", "ELSE"),
    # const
    (r"const", "CONST"),
    # random
    (r"random", "RANDOM"),
    # left brackets
    (r"\[", "LBRACKET"),
    # right brackets
    (r"\]", "RBRACKET"),
    # repeat
    (r"repeat", "REPEAT"),
    # no
    (r"no", "NO"),
    # struct
    (r"struct", "STRUCT"),
    # some
    (r"some", "SOME"),
    # for
    (r"for", "FOR"),
    # in
    (r"in", "IN"),
    # boolean
    (r"boolean", "BOOLEAN"),
    # true
    (r"true", "TRUE"),
    # false
    (r"false", "FALSE"),
    # void
    (r"void", "VOID"),
    # increment
    (r"\+\+", "INCREMENT"),
    # decrement
    (r"--", "DECREMENT"),
    # break
    (r"break", "BREAK"),
    # while
    (r"while", "WHILE"),
    # dot
    (r"\.", "DOT"),
    # length
    (r"\#", "LENGTH"),
    # bitwise complement
    (r"\~", "BITWISE_COMPLEMENT"),
    # not
    (r"\!", "NOT"),
    # left shift
    (r"\<\<", "LEFT_SHIFT"),
    # right shift
    (r"\>\>", "RIGHT_SHIFT"),
    # bitwise and
    (r"\&", "BITWISE_AND"),
    # bitwise or
    (r"\|", "BITWISE_OR"),
    # bitwise xor
    (r"\^", "BITWISE_XOR"),
    # logic or
    (r"\|\|", "LOGICAL_OR"),
    # logic and
    (r"\&\&", "LOGICAL_AND"),
    # codepoints
    (r"codepoints", "CODEPOINTS"),
    # bytes
    (r"bytes", "BYTES"),
    # pi
    (r"\π", "PI"),
    # square root
    (r"sqrt", "SQUARE_ROOT"),
    # sinus
    (r"sin", "SIN"),
    # cosinus
    (r"cos", "COS"),
    # exponenential
    (r"exp", "EXP"),
    # natural log
    (r"ln", "LN"),
    # hypothenuse
    (r"hypot", "HYPOT"),
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
        return self.tag
