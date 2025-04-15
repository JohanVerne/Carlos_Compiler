from Lexer.lexer import Lexem
import logging
from AST import (
    Program,
    VarDecl,
    TypeDecl,
    FunDecl,
    Block,
    IfStmt,
    LoopStmt,
    Literal,
    Identifier,
    Call,
    BinaryOp,
    UnaryOp,
    Expression,
    Statement,
    ArrayAccess,
    MemberAccess,
)

logger = logging.getLogger(__name__)


class ParsingException(Exception):
    pass


class Parser:
    def __init__(self, lexems: list[Lexem]):
        ### Initialize the parser with the lexems
        self.lexems = lexems

    def accept(self):
        # Pop the lexem out of the lexems list
        self.show_next()
        return self.lexems.pop(0)

    def show_next(self, n=1):
        # Returns the next lexem in the lexems list without popping it
        try:
            return self.lexems[n - 1]
        except IndexError:
            raise ParsingException("No more lexems left")

    def expect(self, tag):
        # pops the next lexem from the lexems list and test it's type through the tag
        next_lexem = self.show_next()
        if next_lexem.tag == tag:
            return self.accept()
        else:
            raise ParsingException(
                f"Error at {str(self.show_next().position)}: Expected {tag}, got {next_lexem.tag} instead"
            )

    def parse(self):
        # Main parsing function
        # The parser will crawl through the lexems and call the corresponding function
        # for each lexem
        try:
            return self.parse_program()
        except ParsingException as e:
            logger.exception(e)
            raise

    def parse_program(self):
        # Program = Statement+
        statements = []
        while self.show_next().tag != "EOF":
            if self.show_next().tag == "COMMENTS":
                self.accept()
            else:
                statements.append(self.parse_statement())
        self.expect("EOF")
        return Program(statements)

    def parse_statement(self):
        #     Statement = VarDecl
        # | TypeDecl
        # | FunDecl
        # | Exp9 ("++" | "--") ";" --bump
        # | Exp9 "=" Exp ";" --assign
        # | Exp9_call ";" --call
        # | break ";" --break
        # | return Exp ";" --return
        # | return ";" --shortreturn
        # | IfStmt
        # | LoopStmt

        if self.show_next().tag in ["LET", "CONST"]:
            return self.parse_var_decl()
        elif self.show_next().tag == "STRUCT":
            return self.parse_type_decl()
        elif self.show_next().tag == "FUNCTION":
            return self.parse_fun_decl()
        elif self.show_next().tag == "BREAK":
            self.expect("BREAK")
            self.expect("SEMICOLON")
            return Literal("break")
        elif self.show_next().tag == "RETURN":
            self.expect("RETURN")
            value = None
            if self.show_next().tag != "SEMICOLON":
                value = self.parse_exp()
            self.expect("SEMICOLON")
            return Call("return", [value] if value else [])
        elif self.show_next().tag == "IF":
            return self.parse_if_stmt()
        elif self.show_next().tag in ["WHILE", "FOR", "REPEAT"]:
            return self.parse_loop_stmt()
        elif self.show_next().tag in [
            "PRINT",
            "CODEPOINTS",
            "BYTES",
            "PI",
            "SQRT",
            "SIN",
            "COS",
            "EXP",
            "LN",
            "HYPOT",
            "RANDOM",
        ]:
            # Handle standard library calls
            stdlib_call = self.parse_stdlib()
            self.expect("SEMICOLON")
            return stdlib_call
        else:
            expr = self.parse_exp()
            if self.show_next().tag in ["INCREMENT", "DECREMENT"]:
                op = self.accept().tag
                self.expect("SEMICOLON")
                return Call(op, [expr])
            elif self.show_next().tag == "EQUAL":
                self.accept()
                value = self.parse_exp()
                self.expect("SEMICOLON")
                return Call("assign", [expr, value])
            elif self.show_next().tag == "SEMICOLON":
                self.accept()
                return expr
            else:
                raise ParsingException(
                    f"Error at {str(self.show_next().position)}: Expected statement, got {self.show_next().tag} instead"
                )

    def parse_var_decl(self):
        # VarDecl = (let | const) id "=" Exp ";"
        decl_type = self.accept().tag  # LET or CONST
        identifier = self.expect("IDENTIFIER").value
        self.expect("EQUAL")
        value = self.parse_exp()
        self.expect("SEMICOLON")
        return VarDecl(decl_type, identifier, value)

    def parse_type_decl(self):
        # TypeDecl = struct id "{" Field\* "}"
        self.expect("STRUCT")
        identifier = self.expect("IDENTIFIER").value
        self.expect("LBRACE")
        fields = []
        while self.show_next().tag != "RBRACE":
            fields.append(self.parse_field())
        self.expect("RBRACE")
        return TypeDecl(identifier, fields)

    def parse_field(self):
        # Field = id ":" Type
        identifier = self.expect("IDENTIFIER").value
        self.expect("COLON")
        type_ = self.parse_type()
        return {"identifier": identifier, "type": type_}

    def parse_fun_decl(self):
        # FunDecl = function id Params (":" Type)? Block
        self.expect("FUNCTION")
        identifier = self.expect("IDENTIFIER").value
        params = self.parse_params()
        return_type = None
        if self.show_next().tag == "COLON":
            self.accept()
            return_type = self.parse_type()
        body = self.parse_block()
        return FunDecl(identifier, params, body, return_type)

    def parse_params(self):
        # Params = "(" ListOf<Param, ","> ")"
        self.expect("LPAREN")
        params = []
        while self.show_next().tag != "RPAREN":
            params.append(self.parse_param())
            if self.show_next().tag == "COMMA":
                self.accept()
        self.expect("RPAREN")
        return params

    def parse_param(self):
        # Param = id ":" Type
        identifier = self.expect("IDENTIFIER").value
        self.expect("COLON")
        type_ = self.parse_type()
        return {"identifier": identifier, "type": type_}

    def parse_type(self):
        # Type        = Type "?"                                --optional
        #       | "[" Type "]"                                  --array
        #       | "(" ListOf<Type, ","> ")" "->" Type           --function
        #       | id                                            --id
        list_of_types = ["BOOLEAN", "INT", "FLOAT", "STRING", "ANY", "VOID"]
        if self.show_next().tag == "LBRACKET":
            self.accept()
            inner_type = self.parse_type()
            self.expect("RBRACKET")
            return {"type": "array", "inner_type": inner_type}
        elif self.show_next().tag == "LPAREN":
            self.accept()
            param_types = []
            while self.show_next().tag != "RPAREN":
                param_types.append(self.parse_type())
                if self.show_next().tag == "COMMA":
                    self.accept()
            self.expect("RPAREN")
            self.expect("ARROW")
            return_type = self.parse_type()
            return {
                "type": "function",
                "params": param_types,
                "return_type": return_type,
            }
        elif self.show_next().tag == "IDENTIFIER":
            identifier = self.accept().value
            if self.show_next().tag == "QUESTION_MARK":
                self.accept()
                return {"type": "optional", "base_type": identifier}
            return {"type": "id", "name": identifier}
        else:
            if self.show_next().tag in list_of_types:
                base_type = self.accept().value
                if self.show_next().tag == "QUESTION_MARK":
                    self.accept()
                    return {"type": "optional", "base_type": base_type}
                return {"type": "primitive", "name": base_type}
            else:
                raise ParsingException(
                    f"Error at {str(self.show_next().position)}: Expected type, got {self.show_next().tag} instead"
                )

    def parse_if_stmt(self):
        #     IfStmt = if Exp Block else Block --long
        # | if Exp Block else IfStmt --elsif
        # | if Exp Block --short
        self.expect("IF")
        condition = self.parse_exp()
        then_block = self.parse_block()
        else_block = None
        if self.show_next().tag == "ELSE":
            self.accept()
            if self.show_next().tag == "IF":
                else_block = self.parse_if_stmt()
            else:
                else_block = self.parse_block()
        return IfStmt(condition, then_block, else_block)

    def parse_loop_stmt(self):
        #     LoopStmt = while Exp Block --while
        # | repeat Exp Block --repeat
        # | for id in Exp ("..." | "..<") Exp Block --range
        # | for id in Exp Block --collection
        if self.show_next().tag == "WHILE":
            self.expect("WHILE")
            condition = self.parse_exp()
            body = self.parse_block()
            return LoopStmt("while", condition, body)
        elif self.show_next().tag == "REPEAT":
            self.expect("REPEAT")
            condition = self.parse_exp()
            body = self.parse_block()
            return LoopStmt("repeat", condition, body)
        elif self.show_next().tag == "FOR":
            self.expect("FOR")
            identifier = self.expect("IDENTIFIER").value
            self.expect("IN")
            iterable = self.parse_exp()
            range_end = None
            if self.show_next().tag in ["EXCLUSIVE_RANGE", "INCLUSIVE_RANGE"]:
                range_type = self.accept().tag
                range_end = self.parse_exp()
            body = self.parse_block()
            return LoopStmt(
                "for",
                {"id": identifier, "iterable": iterable, "range_end": range_end},
                body,
            )

    def parse_block(self):
        # Block = "{" Statement\* "}"
        self.expect("LBRACE")
        statements = []
        while self.show_next().tag != "RBRACE":
            statements.append(self.parse_statement())
        self.expect("RBRACE")
        return Block(statements)

    def parse_exp(self):
        #     Exp = Exp1 "?" Exp1 ":" Exp --conditional
        # | Exp1
        expr = self.parse_exp1()
        if self.show_next().tag == "QUESTION_MARK":
            self.accept()
            true_expr = self.parse_exp1()
            self.expect("COLON")
            false_expr = self.parse_exp()
            return Call("conditional", [expr, true_expr, false_expr])
        return expr

    def parse_exp1(self):
        #     Exp1 = Exp1 "??" Exp2 --unwrapelse
        # | Exp2
        expr = self.parse_exp2()
        if self.show_next().tag == "DOUBLE_QUESTION_MARK":
            self.accept()
            fallback_expr = self.parse_exp2()
            return Call("unwrapelse", [expr, fallback_expr])
        return expr

    def parse_exp2(self):
        #     Exp2 = Exp3 ("||" Exp3)+ --or
        # | Exp3 ("&&" Exp3)+ --and
        # | Exp3
        expr = self.parse_exp3()
        while self.show_next().tag in ["LOGICAL_OR", "LOGICAL_AND"]:
            op = self.accept().tag
            right_expr = self.parse_exp3()
            expr = BinaryOp(expr, op, right_expr)
        return expr

    def parse_exp3(self):
        #     Exp3 = Exp4 ("|" Exp4)+ --bitor
        # | Exp4 ("^" Exp4)+ --bitxor
        # | Exp4 ("&" Exp4)+ --bitand
        # | Exp4
        expr = self.parse_exp4()
        while self.show_next().tag in ["BITWISE_OR", "BITWISE_XOR", "BITWISE_AND"]:
            op = self.accept().tag
            right_expr = self.parse_exp4()
            expr = BinaryOp(expr, op, right_expr)
        return expr

    def parse_exp4(self):
        #     Exp4 = Exp5 ("<="|"<"|"=="|"!="|">="|">") Exp5 --compare
        # | Exp5
        expr = self.parse_exp5()
        if self.show_next().tag in [
            "LESS_THAN_EQUAL",
            "LESS_THAN",
            "IS_EQUAL",
            "IS_NOT_EQUAL",
            "GREATER_THAN_EQUAL",
            "GREATER_THAN",
        ]:
            op = self.accept().tag
            right_expr = self.parse_exp5()
            expr = BinaryOp(expr, op, right_expr)
        return expr

    def parse_exp5(self):
        #     Exp5 = Exp5 ("<<" | ">>") Exp6 --shift
        # | Exp6
        expr = self.parse_exp6()
        while self.show_next().tag in ["LEFT_SHIFT", "RIGHT_SHIFT"]:
            op = self.accept().tag
            right_expr = self.parse_exp6()
            expr = BinaryOp(expr, op, right_expr)
        return expr

    def parse_exp6(self):
        #     Exp6 = Exp6 ("+" | "-") Exp7 --add
        # | Exp7
        expr = self.parse_exp7()
        while self.show_next().tag in ["PLUS", "MINUS"]:
            op = self.accept().tag
            right_expr = self.parse_exp7()
            expr = BinaryOp(expr, op, right_expr)
        return expr

    def parse_exp7(self):
        #     Exp7 = Exp7 ("*"| "/" | "%") Exp8 --multiply
        # | Exp8
        expr = self.parse_exp8()
        while self.show_next().tag in ["MULTIPLICATION", "DIVISION", "MODULO"]:
            op = self.accept().tag
            right_expr = self.parse_exp8()
            expr = BinaryOp(expr, op, right_expr)
        return expr

    def parse_exp8(self):
        #     Exp8 = Exp9 "\*\*" Exp8 --power
        # | Exp9
        # | ("#" | "-" | "!" | some | random) Exp9 --unary
        if self.show_next().tag in ["LENGTH", "MINUS", "NOT", "SOME", "RANDOM"]:
            op = self.accept().tag
            operand = self.parse_exp9()
            return UnaryOp(op, operand)
        expr = self.parse_exp9()
        if self.show_next().tag == "POWER":
            self.accept()
            right_expr = self.parse_exp8()
            return BinaryOp(expr, "POWER", right_expr)
        return expr

    def parse_exp9(self):
        #     Exp9 = true ~mut
        # | false ~mut
        # | floatlit ~mut
        # | intlit ~mut
        # | no Type ~mut --emptyopt
        # | Exp9 "(" ListOf<Exp, ","> ")" ~mut --call
        # | Exp9 "[" Exp "]" --subscript
        # | Exp9 ("." | "?.") id --member
        # | stringlit ~mut
        # | id --id
        # | Type_array "(" ")" ~mut --emptyarray  ///FIXME : Not implemented because ambiguous with next one
        # | "[" NonemptyListOf<Exp, ","> "]" ~mut --arrayexp
        # | "(" Exp ")" ~mut --parens

        if self.show_next().tag in [
            "TRUE",
            "FALSE",
            "FLOAT_LITERAL",
            "INTEGER_LITERAL",
            "STRING_LITERAL",
        ]:
            return Literal(self.accept().value)

        elif self.show_next().tag == "NO":
            self.accept()
            type_ = self.parse_type()
            return Call("emptyopt", [type_])

        elif self.show_next().tag == "LBRACKET":
            self.accept()
            elements = []
            while self.show_next().tag != "RBRACKET":
                elements.append(self.parse_exp())
                if self.show_next().tag == "COMMA":
                    self.accept()
            self.expect("RBRACKET")
            return Call("array", elements)

        elif self.show_next().tag == "LPAREN":
            self.accept()
            expr = self.parse_exp()  # Parse the nested expression
            self.expect("RPAREN")  # Ensure the closing parenthesis is present
            return expr

        elif self.show_next().tag == "IDENTIFIER":
            identifier = Identifier(self.accept().value)

            if self.show_next().tag == "LPAREN":
                self.accept()
                arguments = []
                while self.show_next().tag != "RPAREN":
                    arguments.append(self.parse_exp())
                    if self.show_next().tag == "COMMA":
                        self.accept()
                self.expect("RPAREN")
                return Call(identifier, arguments)

            elif self.show_next().tag == "LBRACKET":
                self.accept()
                index = self.parse_exp()
                self.expect("RBRACKET")
                return ArrayAccess(identifier, index)

            elif self.show_next().tag in ["DOT", "OPTIONAL_MEMBER"]:
                op = self.accept().tag
                member = self.expect("IDENTIFIER").value
                return MemberAccess(identifier, member, op == "OPTIONAL_MEMBER")

            return identifier
        else:
            raise ParsingException(
                f"Error at {str(self.show_next().position)}: unexpected token : {self.show_next().tag}"
            )

    def parse_stdlib(self):
        # function print(s: any): void

        # Writes a representation of s

        # to standard output.
        # function codepoints(s: string): [int]

        # Returns the code points of the s

        # .
        # function bytes(s: string): [int]

        # Returns the bytes of the UTF-8 encoding of s

        # .
        # const π

        # Returns the best approximate value of pi

        # in the type float.
        # function sqrt(x: float): float

        # Returns the square root of x

        # .
        # function sin(x: float): float

        # Returns the sine of x

        # radians.
        # function cos(x: float): float

        # Returns the cosine of x

        # radians.
        # function exp(x: float): float

        # Returns e^x

        # .
        # function ln(x: float): float

        # Returns the natural log of x

        # .
        # function hypot(x: float, y: float): float

        # Returns the hypotenuse of a right triangle with sides |x|
        # and |y|.

        # function random(a : array<any>): any
        # Returns a random element of a.
        if self.show_next().tag == "PRINT":
            self.accept()
            self.expect("LPAREN")
            arguments = []
            while self.show_next().tag != "RPAREN":
                arguments.append(self.parse_exp())
                if self.show_next().tag == "COMMA":
                    self.accept()
            self.expect("RPAREN")
            return Call("print", arguments)

        elif self.show_next().tag == "CODEPOINTS":
            self.accept()
            self.expect("LPAREN")
            string_expr = self.parse_exp()
            self.expect("RPAREN")
            return Call("codepoints", [string_expr])

        elif self.show_next().tag == "BYTES":
            self.accept()
            self.expect("LPAREN")
            string_expr = self.parse_exp()
            self.expect("RPAREN")
            return Call("bytes", [string_expr])

        elif self.show_next().tag == "PI":
            self.accept()
            return Literal("pi")

        elif self.show_next().tag in ["SQRT", "SIN", "COS", "EXP", "LN"]:
            func_name = self.accept().tag.lower()
            self.expect("LPAREN")
            argument = self.parse_exp()
            self.expect("RPAREN")
            return Call(func_name, [argument])

        elif self.show_next().tag == "HYPOT":
            self.accept()
            self.expect("LPAREN")
            arg1 = self.parse_exp()
            self.expect("COMMA")
            arg2 = self.parse_exp()
            self.expect("RPAREN")
            return Call("hypot", [arg1, arg2])

        elif self.show_next().tag == "RANDOM":
            self.accept()
            self.expect("LPAREN")
            array_expr = self.parse_exp()
            self.expect("RPAREN")
            return Call("random", [array_expr])

        else:
            raise ParsingException(
                f"Error at {str(self.show_next().position)}: Expected standard library function, got {self.show_next().tag} instead"
            )
