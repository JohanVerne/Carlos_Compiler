from Parser.AST import *


class PrettyPrinter:
    """
    A visitor class that traverses the AST and produces the original source code.
    """

    def __init__(self):
        self.indent_level = 0
        self.indent_str = "  "  # Two spaces per indent level

    def get_indent(self):
        """Return the current indentation string"""
        return self.indent_str * self.indent_level

    def visit_Program(self, node):
        """Visit a Program node, which is the root of the AST"""
        result = ""
        # Visit each statement in the program body
        for stmt in node.body:
            result += stmt.accept(self)
            # Add newline if not already there
            if not result.endswith("\n"):
                result += "\n"
            # Add extra newline between top-level statements for readability
            result += "\n"

        # Remove extra newlines at the end
        return result.rstrip() + "\n"

    def visit_VarDecl(self, node):
        """Visit a variable declaration"""
        decl_type = "let" if node.decl_statement == "LET" else "const"
        return f"{self.get_indent()}{decl_type} {node.identifier} = {node.value.accept(self)};"

    def visit_TypeDecl(self, node):
        """Visit a type declaration (struct)"""
        result = f"{self.get_indent()}struct {node.identifier} {{\n"
        self.indent_level += 1

        for field in node.fields:
            result += f"{self.get_indent()}{field['identifier']}: {self._format_type(field['type'])}\n"

        self.indent_level -= 1
        result += f"{self.get_indent()}}}"

        return result

    def _format_type(self, type_info):
        """Helper method to format type information"""
        if isinstance(type_info, dict):
            if type_info.get("type") == "array":
                return f"[{self._format_type(type_info.get('inner_type'))}]"
            elif type_info.get("type") == "function":
                params = ", ".join(
                    [self._format_type(param) for param in type_info.get("params", [])]
                )
                return (
                    f"({params}) -> {self._format_type(type_info.get('return_type'))}"
                )
            elif type_info.get("type") == "optional":
                return f"{type_info.get('base_type')}?"
            elif type_info.get("type") == "id":
                return type_info.get("name")
            elif type_info.get("type") == "primitive":
                return type_info.get("name")
        return str(type_info)

    def visit_FunDecl(self, node):
        """Visit a function declaration"""
        # Format parameters
        params = []
        for param in node.params:
            params.append(f"{param['identifier']}: {self._format_type(param['type'])}")

        param_str = ", ".join(params)

        # Include return type if specified
        return_type_str = ""
        if node.return_type:
            return_type_str = f": {self._format_type(node.return_type)}"

        result = f"{self.get_indent()}function {node.identifier}({param_str}){return_type_str} "
        result += node.body.accept(self)

        return result

    def visit_Block(self, node):
        """Visit a block of statements"""
        if not node.statements:
            return "{}"

        result = "{\n"
        self.indent_level += 1

        for stmt in node.statements:
            stmt_code = stmt.accept(self)
            result += f"{stmt_code}\n"

        self.indent_level -= 1
        result += f"{self.get_indent()}}}"

        return result

    def visit_IfStmt(self, node):
        """Visit an if statement"""
        result = f"{self.get_indent()}if {node.condition.accept(self)} "
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
            result = f"{self.get_indent()}while {node.condition.accept(self)} "
        elif node.loop_type == "repeat":
            result = f"{self.get_indent()}repeat {node.condition.accept(self)} "
        elif node.loop_type == "for":
            # Handle for loop with different formats
            if isinstance(node.condition, dict):
                id_name = node.condition.get("id", "")
                iterable = node.condition.get("iterable").accept(self)
                range_end = node.condition.get("range_end")

                result = f"{self.get_indent()}for {id_name} in {iterable}"
                if range_end:
                    # Determine if inclusive or exclusive range (this is a guess, would need tag info)
                    range_operator = "..." if "..." in str(node.condition) else "..<"
                    result += f" {range_operator} {range_end.accept(self)}"
            else:
                # Generic fallback
                result = f"{self.get_indent()}for {node.condition.accept(self)} "
        else:
            # Fallback for unknown loop types
            result = (
                f"{self.get_indent()}{node.loop_type} {node.condition.accept(self)} "
            )

        result += node.body.accept(self)
        return result

    def _get_op_string(self, op):
        """Convert operator tag to actual operator string"""
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
            "IS_EQUAL": "==",
            "IS_NOT_EQUAL": "!=",
            "GREATER_THAN_EQUAL": ">=",
            "GREATER_THAN": ">",
            "DOUBLE_QUESTION_MARK": "??",
        }
        return op_map.get(op, op.lower())

    def _need_parens(self, parent_op, child_op, is_left=True):
        """
        Determine if parentheses are needed based on operator precedence and associativity
        This is a simplified version and would need to be expanded with actual operator precedence
        """
        precedence = {
            "POWER": 14,
            "MULTIPLICATION": 13,
            "DIVISION": 13,
            "MODULO": 13,
            "PLUS": 12,
            "MINUS": 12,
            "LEFT_SHIFT": 11,
            "RIGHT_SHIFT": 11,
            "LESS_THAN": 10,
            "LESS_THAN_EQUAL": 10,
            "GREATER_THAN": 10,
            "GREATER_THAN_EQUAL": 10,
            "IS_EQUAL": 9,
            "IS_NOT_EQUAL": 9,
            "BITWISE_AND": 8,
            "BITWISE_XOR": 7,
            "BITWISE_OR": 6,
            "LOGICAL_AND": 5,
            "LOGICAL_OR": 4,
            "DOUBLE_QUESTION_MARK": 3,
            "CONDITIONAL": 2,
            "ASSIGNMENT": 1,
        }

        if parent_op not in precedence or child_op not in precedence:
            return True

        if precedence[parent_op] > precedence[child_op]:
            return True

        # Handle right-associative operators like power (**)
        if precedence[parent_op] == precedence[child_op]:
            if parent_op == "POWER" and not is_left:
                return False
            return not is_left

        return False

    def visit_BinaryOp(self, node):
        """Visit a binary operation"""
        op_str = self._get_op_string(node.op)

        # Check if left operand needs parentheses
        lhs_str = node.lhs.accept(self)
        if isinstance(node.lhs, BinaryOp) and self._need_parens(
            node.op, node.lhs.op, True
        ):
            lhs_str = f"({lhs_str})"

        # Check if right operand needs parentheses
        rhs_str = node.rhs.accept(self)
        if isinstance(node.rhs, BinaryOp) and self._need_parens(
            node.op, node.rhs.op, False
        ):
            rhs_str = f"({rhs_str})"

        return f"{lhs_str} {op_str} {rhs_str}"

    def visit_UnaryOp(self, node):
        """Visit a unary operation"""
        op_map = {
            "MINUS": "-",
            "NOT": "!",
            "LENGTH": "#",
            "SOME": "some",
            "RANDOM": "random",
        }

        op_str = op_map.get(node.operator, node.operator.lower())
        operand_str = node.operand.accept(self)

        # Add parentheses if needed
        if not isinstance(node.operand, (Literal, Identifier)):
            operand_str = f"({operand_str})"

        if op_str in ["some", "random"]:
            return f"{op_str} {operand_str}"
        return f"{op_str}{operand_str}"

    def visit_Literal(self, node):
        """Visit a literal value"""
        # Handle string literals by adding quotes
        if isinstance(node.value, str) and node.value not in [
            "true",
            "false",
            "pi",
            "break",
        ]:
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
                    return f"{self.get_indent()}return;"
                return f"{self.get_indent()}return {node.arguments[0].accept(self)};"

            elif node.callee == "assign":
                lhs = node.arguments[0].accept(self)
                rhs = node.arguments[1].accept(self)
                return f"{self.get_indent()}{lhs} = {rhs};"

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
                type_str = self._format_type(node.arguments[0])
                return f"no {type_str}"

            elif node.callee in ["INCREMENT", "DECREMENT"]:
                op = "++" if node.callee == "INCREMENT" else "--"
                return f"{self.get_indent()}{node.arguments[0].accept(self)}{op};"

            # Handle standard library functions
            elif node.callee in [
                "print",
                "codepoints",
                "bytes",
                "sqrt",
                "sin",
                "cos",
                "exp",
                "ln",
                "hypot",
                "random",
            ]:
                args = [
                    arg.accept(self) if hasattr(arg, "accept") else str(arg)
                    for arg in node.arguments
                ]
                return f"{self.get_indent()}{node.callee}({', '.join(args)})"

        # Regular function call
        if isinstance(node.callee, Identifier):
            func_name = node.callee.name
        else:
            func_name = node.callee.accept(self)

        args = []
        for arg in node.arguments:
            if arg is None:
                continue
            if hasattr(arg, "accept"):
                args.append(arg.accept(self))
            else:
                args.append(str(arg))

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
