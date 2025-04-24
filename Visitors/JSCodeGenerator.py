import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
sys.path.append(parent_dir)
sys.path.append(os.path.join(parent_dir, "Parser"))  # Add Parser directory to path

from Parser.parser import Parser
from Lexer.lexer import Lexer
from Parser.AST import *


class JSCodeGenerator:
    """
    A visitor class that traverses the AST and generates equivalent JavaScript code.
    """

    def __init__(self):
        self.indent_level = 0
        self.indent_str = "  "  # Two spaces per indent level

    def get_indent(self):
        """Return the current indentation string"""
        return self.indent_str * self.indent_level

    def visit_Program(self, node):
        """Visit a Program node, which is the root of the AST"""
        result = "// Generated JavaScript from Carlos\n\n"

        # Visit each statement in the program body
        for stmt in node.body:
            stmt_code = stmt.accept(self)
            result += stmt_code

            # Add newline if not already there
            if not result.endswith("\n"):
                result += "\n"

            # Add extra newline between top-level statements for readability
            result += "\n"

        # Remove extra newlines at the end
        return result.rstrip() + "\n"

    def visit_VarDecl(self, node):
        """Visit a variable declaration"""
        # Map 'LET' to 'let' and 'CONST' to 'const'
        decl_type = "let" if node.decl_statement == "LET" else "const"
        return f"{self.get_indent()}{decl_type} {node.identifier} = {node.value.accept(self)};"

    def visit_TypeDecl(self, node):
        """Visit a type declaration (struct)"""
        # In JavaScript, we'll define a class with a constructor to represent structs
        result = f"{self.get_indent()}class {node.identifier} {{\n"
        self.indent_level += 1

        # Add constructor
        result += f"{self.get_indent()}constructor("
        params = []
        assignments = []

        for field in node.fields:
            field_name = field["identifier"]
            params.append(field_name)
            assignments.append(
                f"{self.get_indent()}{self.indent_str}this.{field_name} = {field_name};"
            )

        result += ", ".join(params)
        result += ") {\n"

        if assignments:
            result += "\n".join(assignments) + "\n"

        result += f"{self.get_indent()}}}\n"
        self.indent_level -= 1
        result += f"{self.get_indent()}}}"

        return result

    def visit_FunDecl(self, node):
        """Visit a function declaration"""
        # Format parameters
        params = []
        for param in node.params:
            params.append(f"{param['identifier']}")

        param_str = ", ".join(params)

        result = f"{self.get_indent()}function {node.identifier}({param_str}) "

        # Visit the function body
        body_code = node.body.accept(self)
        result += body_code

        return result

    def visit_Block(self, node):
        """Visit a block of statements"""
        if not node.statements:
            return "{}"

        result = "{\n"
        self.indent_level += 1

        for stmt in node.statements:
            stmt_code = stmt.accept(self)
            if not stmt_code.endswith(";") and not stmt_code.endswith("}"):
                stmt_code += ";"
            result += f"{stmt_code}\n"

        self.indent_level -= 1
        result += f"{self.get_indent()}}}"

        return result

    def visit_IfStmt(self, node):
        """Visit an if statement"""
        result = f"{self.get_indent()}if ({node.condition.accept(self)}) "
        result += node.then_block.accept(self)

        if node.else_block:
            result += f" else "
            # Handle else-if chains
            if isinstance(node.else_block, IfStmt):
                # Remove the indent for chained else-if
                else_code = node.else_block.accept(self)
                result += else_code.lstrip()
            else:
                result += node.else_block.accept(self)

        return result

    def visit_LoopStmt(self, node):
        """Visit a loop statement (while, for, repeat)"""
        if node.loop_type == "while":
            result = f"{self.get_indent()}while ({node.condition.accept(self)}) "
        elif node.loop_type == "repeat":
            # For "repeat n times" pattern, we'll use a traditional for loop in JavaScript
            result = f"{self.get_indent()}for (let _i = 0; _i < {node.condition.accept(self)}; _i++) "
        elif node.loop_type == "for":
            # Handle for loop with different formats
            if isinstance(node.condition, dict):
                id_name = node.condition.get("id", "")
                iterable = node.condition.get("iterable").accept(self)
                range_end = node.condition.get("range_end")

                if range_end:
                    # Map range-based for loops to JavaScript for loops
                    range_operator = node.condition.get("range_operator", "...<")
                    inclusive = range_operator == "..."

                    # Create appropriate loop based on the range type
                    result = f"{self.get_indent()}for (let {id_name} = {iterable}; "

                    if inclusive:
                        result += f"{id_name} <= {range_end.accept(self)}; "
                    else:
                        result += f"{id_name} < {range_end.accept(self)}; "

                    result += f"{id_name}++) "
                else:
                    # For-in loops for collections
                    # In JavaScript, you'd typically use for...of for iteration
                    result = f"{self.get_indent()}for (const {id_name} of {iterable}) "
            else:
                # Generic fallback
                result = f"{self.get_indent()}for ({node.condition.accept(self)}) "
        else:
            # Fallback for unknown loop types
            result = f"{self.get_indent()}// Unsupported loop type: {node.loop_type}\n"
            result += f"{self.get_indent()}while ({node.condition.accept(self)}) "

        result += node.body.accept(self)
        return result

    def _js_op(self, op):
        """Convert Carlos operator tag to JavaScript operator"""
        op_map = {
            "PLUS": "+",
            "MINUS": "-",
            "MULTIPLICATION": "*",
            "DIVISION": "/",
            "MODULO": "%",
            "POWER": "**",
            "LOGICAL_OR": "||",
            "LOGICAL_AND": "&&",
            "BITWISE_OR": "|",
            "BITWISE_XOR": "^",
            "BITWISE_AND": "&",
            "LEFT_SHIFT": "<<",
            "RIGHT_SHIFT": ">>",
            "LESS_THAN_EQUAL": "<=",
            "LESS_THAN": "<",
            "IS_EQUAL": "===",
            "IS_NOT_EQUAL": "!==",
            "GREATER_THAN_EQUAL": ">=",
            "GREATER_THAN": ">",
            "DOUBLE_QUESTION_MARK": "??",
        }
        return op_map.get(op, op.lower())

    def visit_BinaryOp(self, node):
        """Visit a binary operation"""
        op_str = self._js_op(node.op)

        # Handle special cases
        if (
            node.op == "POWER"
            and isinstance(node.lhs, Literal)
            and isinstance(node.rhs, Literal)
        ):
            # For simple literal power operations, use Math.pow
            return f"Math.pow({node.lhs.accept(self)}, {node.rhs.accept(self)})"

        # Get operands
        lhs_str = node.lhs.accept(self)
        rhs_str = node.rhs.accept(self)

        # Add parentheses for complex expressions
        if isinstance(node.lhs, BinaryOp):
            lhs_str = f"({lhs_str})"

        if isinstance(node.rhs, BinaryOp):
            rhs_str = f"({rhs_str})"

        return f"{lhs_str} {op_str} {rhs_str}"

    def visit_UnaryOp(self, node):
        """Visit a unary operation"""
        op_map = {
            "MINUS": "-",
            "NOT": "!",
            "LENGTH": "",  # Handle length specially
            "SOME": "",  # Handle 'some' specially
            "RANDOM": "",  # Handle 'random' specially
        }

        op_str = op_map.get(node.operator, node.operator.lower())

        # Special case for 'some' operator with constructor calls
        if (
            node.operator == "SOME"
            and isinstance(node.operand, Call)
            and isinstance(node.operand.callee, Identifier)
        ):
            # Handle constructor calls directly by adding 'new'
            func_name = node.operand.callee.name
            args = []
            for arg in node.operand.arguments:
                if arg is None:
                    continue
                if hasattr(arg, "accept"):
                    args.append(arg.accept(self))
                else:
                    args.append(str(arg))

            return f"new {func_name}({', '.join(args)})"

        operand_str = node.operand.accept(self)

        # Special case for length operator
        if node.operator == "LENGTH":
            if isinstance(node.operand, Identifier) or isinstance(
                node.operand, MemberAccess
            ):
                return f"{operand_str}.length"
            else:
                return f"({operand_str}).length"

        # Special case for 'some' operator (typically used for optionals)
        elif node.operator == "SOME":
            return operand_str  # In JS, we don't need a special operator

        # Special case for 'random' operator
        elif node.operator == "RANDOM":
            if isinstance(node.operand, Identifier) or isinstance(
                node.operand, MemberAccess
            ):
                return (
                    f"{operand_str}[Math.floor(Math.random() * {operand_str}.length)]"
                )
            else:
                return f"(() => {{ const _arr = {operand_str}; return _arr[Math.floor(Math.random() * _arr.length)]; }})()"

        # Add parentheses if needed
        if not isinstance(node.operand, (Literal, Identifier)):
            operand_str = f"({operand_str})"

        return f"{op_str}{operand_str}"

    def visit_Literal(self, node):
        """Visit a literal value"""
        # Handle special literals
        if node.value == "pi":
            return "Math.PI"
        elif node.value == "break":
            return f"{self.get_indent()}break"

        # Handle numeric literals
        if isinstance(node.value, (float, int)):
            return str(node.value)

        # Handle string literals
        if isinstance(node.value, str):
            if node.value in ["true", "false"]:
                return node.value

            # Check if it's a number represented as a string
            try:
                # Try to parse as a float first
                float_value = float(node.value)
                # If it's an integer value, return without decimal point
                if float_value.is_integer():
                    return str(int(float_value))
                return str(float_value)
            except ValueError:
                # Not a number, it's a regular string
                # Check if already has quotes
                if not (node.value.startswith('"') and node.value.endswith('"')):
                    return f'"{node.value}"'

        return str(node.value)

    def visit_Identifier(self, node):
        """Visit an identifier"""
        return node.name

    def visit_Call(self, node):
        """Visit a function call"""
        # Handle special calls that map to language constructs
        if isinstance(node.callee, str):
            if node.callee == "return":
                if not node.arguments or node.arguments[0] is None:
                    return f"{self.get_indent()}return"
                return f"{self.get_indent()}return {node.arguments[0].accept(self)}"

            elif node.callee == "assign":
                lhs = node.arguments[0].accept(self)
                rhs = node.arguments[1].accept(self)
                return f"{self.get_indent()}{lhs} = {rhs}"

            elif node.callee == "conditional":
                condition = node.arguments[0].accept(self)
                true_expr = node.arguments[1].accept(self)
                false_expr = node.arguments[2].accept(self)
                return f"{condition} ? {true_expr} : {false_expr}"

            elif node.callee == "unwrapelse":
                expr = node.arguments[0].accept(self)
                fallback = node.arguments[1].accept(self)
                return f"{expr} ?? {fallback}"

            elif node.callee == "array":
                elements = [arg.accept(self) for arg in node.arguments]
                return f"[{', '.join(elements)}]"

            elif node.callee == "emptyopt":
                # 'no Type' maps to null in JavaScript
                return "null"

            elif node.callee in ["INCREMENT", "DECREMENT"]:
                op = "++" if node.callee == "INCREMENT" else "--"
                return f"{self.get_indent()}{node.arguments[0].accept(self)}{op}"

            # Handle standard library functions
            elif node.callee == "print":
                args = [
                    arg.accept(self) if hasattr(arg, "accept") else str(arg)
                    for arg in node.arguments
                ]
                return f"{self.get_indent()}console.log({', '.join(args)})"

            elif node.callee == "codepoints":
                arg = node.arguments[0].accept(self)
                return f"[...{arg}].map(c => c.codePointAt(0))"

            elif node.callee == "bytes":
                arg = node.arguments[0].accept(self)
                return f"new TextEncoder().encode({arg})"

            elif node.callee == "sqrt":
                arg = node.arguments[0].accept(self)
                return f"Math.sqrt({arg})"

            elif node.callee == "sin":
                arg = node.arguments[0].accept(self)
                return f"Math.sin({arg})"

            elif node.callee == "cos":
                arg = node.arguments[0].accept(self)
                return f"Math.cos({arg})"

            elif node.callee == "exp":
                arg = node.arguments[0].accept(self)
                return f"Math.exp({arg})"

            elif node.callee == "ln":
                arg = node.arguments[0].accept(self)
                return f"Math.log({arg})"

            elif node.callee == "hypot":
                args = [arg.accept(self) for arg in node.arguments]
                return f"Math.hypot({', '.join(args)})"

            elif node.callee == "random":
                arg = node.arguments[0].accept(self)
                return f"{arg}[Math.floor(Math.random() * {arg}.length)]"

        # Regular function call
        if isinstance(node.callee, Identifier):
            func_name = node.callee.name
            # Check if this is likely a struct constructor call (capital first letter is a convention)
            is_struct_constructor = func_name[0].isupper() if func_name else False
        else:
            func_name = node.callee.accept(self)
            is_struct_constructor = (
                False  # Cannot reliably determine for non-identifiers
            )

        args = []
        for arg in node.arguments:
            if arg is None:
                continue
            if hasattr(arg, "accept"):
                args.append(arg.accept(self))
            else:
                args.append(str(arg))

        # Add 'new' keyword for struct constructor calls
        if is_struct_constructor:
            return f"new {func_name}({', '.join(args)})"
        else:
            return f"{func_name}({', '.join(args)})"

    def visit_MemberAccess(self, node):
        """Visit a member access expression"""
        obj_str = node.object_.accept(self)
        op_str = "?." if node.op else "."

        # Add parentheses if needed
        if not isinstance(node.object_, (Literal, Identifier, MemberAccess)):
            obj_str = f"({obj_str})"

        return f"{obj_str}{op_str}{node.member}"

    def visit_ArrayAccess(self, node):
        """Visit an array access expression"""
        array_str = node.array.accept(self)
        index_str = node.index.accept(self)

        # Add parentheses if needed
        if not isinstance(node.array, (Literal, Identifier, MemberAccess, ArrayAccess)):
            array_str = f"({array_str})"

        return f"{array_str}[{index_str}]"

    def visit_Statement(self, node):
        """Generic visit for Statement nodes"""
        return f"{self.get_indent()}// Unknown statement: {type(node).__name__}"

    def visit_Expression(self, node):
        """Generic visit for Expression nodes"""
        return f"/* Unknown expression: {type(node).__name__} */"


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 JSCodeGenerator.py <input_file.carlos> [--save]")
        sys.exit(1)

    input_file = sys.argv[1]
    save_js = "--save" in sys.argv  # Save only if --save is explicitly provided

    # Ensure the input file has the correct extension
    if not input_file.endswith(".carlos"):
        print("Error: Input file must have a .carlos extension.")
        sys.exit(1)

    # Read the input file
    try:
        with open(input_file, "r") as file:
            input_text = file.readlines()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)

    # Step 1: Lexing
    lexer = Lexer()
    try:
        lexems = lexer.lex(input_text)
    except Exception as e:
        print(f"Lexing failed: {e}")
        sys.exit(1)

    # Step 2: Parsing
    parser = Parser(lexems)
    try:
        ast = parser.parse()
    except Exception as e:
        print(f"Parsing failed: {e}")
        sys.exit(1)

    # Step 3: JavaScript Code Generation
    generator = JSCodeGenerator()
    try:
        js_code = ast.accept(generator)
    except Exception as e:
        print(f"Code generation failed: {e}")
        sys.exit(1)

    # Print the generated JavaScript code to the terminal
    print("Generated JavaScript Code:")
    print(js_code)

    # Save the JavaScript code to a file if --save is provided
    if save_js:
        # Ensure the Visitors/examples_js directory exists
        output_dir = os.path.join(
            os.path.dirname(input_file), "../Visitors/examples_js"
        )
        os.makedirs(output_dir, exist_ok=True)

        # Save the JavaScript code in the examples_js directory
        output_file = os.path.join(
            output_dir, os.path.basename(input_file).replace(".carlos", ".js")
        )
        try:
            with open(output_file, "w") as file:
                file.write(js_code)
            print(f"JavaScript file saved to: {output_file}")
        except Exception as e:
            print(f"Failed to save JavaScript file: {e}")
            sys.exit(1)
