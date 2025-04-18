from Parser.AST import *


class ASTPrinter:
    """
    A visitor class that traverses the AST and produces a string representation.
    This visitor implements the accept method for each node type.
    """

    def __init__(self):
        self.indent_level = 0
        self.indent_str = "  "  # Two spaces per indent level

    def get_indent(self):
        """Return the current indentation string"""
        return self.indent_str * self.indent_level

    def visit_Program(self, node):
        """Visit a Program node, which is the root of the AST"""
        result = "Program:\n"
        self.indent_level += 1

        # Visit each statement in the program body
        for stmt in node.body:
            result += self.get_indent() + stmt.accept(self)

        self.indent_level -= 1
        return result

    def visit_VarDecl(self, node):
        """Visit a variable declaration"""
        result = f"VarDecl ({node.decl_statement}):\n"
        self.indent_level += 1

        result += self.get_indent() + f"Identifier: {node.identifier}\n"
        result += self.get_indent() + "Value:\n"

        self.indent_level += 1
        result += self.get_indent() + node.value.accept(self)
        self.indent_level -= 2

        return result

    def visit_TypeDecl(self, node):
        """Visit a type declaration (struct)"""
        result = f"TypeDecl: {node.identifier}\n"
        self.indent_level += 1

        result += self.get_indent() + "Fields:\n"
        self.indent_level += 1

        for field in node.fields:
            result += (
                self.get_indent() + f"Field: {field['identifier']} : {field['type']}\n"
            )

        self.indent_level -= 2
        return result

    def visit_FunDecl(self, node):
        """Visit a function declaration"""
        result = f"FunDecl: {node.identifier}\n"
        self.indent_level += 1

        # Handle parameters
        result += self.get_indent() + "Parameters:\n"
        self.indent_level += 1
        for param in node.params:
            result += (
                self.get_indent() + f"Param: {param['identifier']} : {param['type']}\n"
            )
        self.indent_level -= 1

        # Handle return type if specified
        if node.return_type:
            result += self.get_indent() + f"Return Type: {node.return_type}\n"

        # Handle body
        result += self.get_indent() + "Body:\n"
        self.indent_level += 1
        result += self.get_indent() + node.body.accept(self)
        self.indent_level -= 2

        return result

    def visit_Block(self, node):
        """Visit a block of statements"""
        result = "Block:\n"
        self.indent_level += 1

        for stmt in node.statements:
            result += self.get_indent() + stmt.accept(self)

        self.indent_level -= 1
        return result

    def visit_IfStmt(self, node):
        """Visit an if statement"""
        result = "IfStmt:\n"
        self.indent_level += 1

        result += self.get_indent() + "Condition:\n"
        self.indent_level += 1
        result += self.get_indent() + node.condition.accept(self)
        self.indent_level -= 1

        result += self.get_indent() + "Then Block:\n"
        self.indent_level += 1
        result += self.get_indent() + node.then_block.accept(self)
        self.indent_level -= 1

        if node.else_block:
            result += self.get_indent() + "Else Block:\n"
            self.indent_level += 1
            result += self.get_indent() + node.else_block.accept(self)
            self.indent_level -= 1

        self.indent_level -= 1
        return result

    def visit_LoopStmt(self, node):
        """Visit a loop statement (while, for, repeat)"""
        result = f"LoopStmt ({node.loop_type}):\n"
        self.indent_level += 1

        result += self.get_indent() + "Condition:\n"
        self.indent_level += 1

        if isinstance(node.condition, dict) and node.loop_type == "for":
            # Special case for for loops
            result += self.get_indent() + f"Identifier: {node.condition['id']}\n"
            result += self.get_indent() + "Iterable:\n"
            self.indent_level += 1
            result += self.get_indent() + node.condition["iterable"].accept(self)
            self.indent_level -= 1

            if node.condition["range_end"]:
                result += self.get_indent() + "Range End:\n"
                self.indent_level += 1
                result += self.get_indent() + node.condition["range_end"].accept(self)
                self.indent_level -= 1
        else:
            result += self.get_indent() + node.condition.accept(self)

        self.indent_level -= 1

        result += self.get_indent() + "Body:\n"
        self.indent_level += 1
        result += self.get_indent() + node.body.accept(self)
        self.indent_level -= 2

        return result

    def visit_BinaryOp(self, node):
        """Visit a binary operation"""
        result = f"BinaryOp ({node.op}):\n"
        self.indent_level += 1

        result += self.get_indent() + "Left:\n"
        self.indent_level += 1
        result += self.get_indent() + node.lhs.accept(self)
        self.indent_level -= 1

        result += self.get_indent() + "Right:\n"
        self.indent_level += 1
        result += self.get_indent() + node.rhs.accept(self)
        self.indent_level -= 2

        return result

    def visit_UnaryOp(self, node):
        """Visit a unary operation"""
        result = f"UnaryOp ({node.operator}):\n"
        self.indent_level += 1

        result += self.get_indent() + "Operand:\n"
        self.indent_level += 1
        result += self.get_indent() + node.operand.accept(self)
        self.indent_level -= 2

        return result

    def visit_Literal(self, node):
        """Visit a literal value"""
        return f"Literal: {node.value}\n"

    def visit_Identifier(self, node):
        """Visit an identifier"""
        return f"Identifier: {node.name}\n"

    def visit_Call(self, node):
        """Visit a function call"""
        if isinstance(node.callee, str):
            # Handle built-in functions or statements that are represented as calls
            result = f"Call: {node.callee}\n"
        else:
            result = "Call:\n"
            self.indent_level += 1
            result += self.get_indent() + "Callee:\n"
            self.indent_level += 1
            result += self.get_indent() + node.callee.accept(self)
            self.indent_level -= 2

        self.indent_level += 1
        result += self.get_indent() + "Arguments:\n"
        self.indent_level += 1

        for arg in node.arguments:
            if arg is None:  # Skip None arguments (e.g., for empty return statements)
                continue

            # Handle different types of arguments
            if hasattr(arg, "accept"):
                result += self.get_indent() + arg.accept(self)
            elif isinstance(arg, dict):
                # Handle dictionary arguments (like types)
                result += self.get_indent() + f"Dictionary: {arg}\n"
            else:
                result += self.get_indent() + f"Value: {arg}\n"

        self.indent_level -= 2

        return result

    def visit_MemberAccess(self, node):
        """Visit a member access expression"""
        op_str = "?." if node.op else "."
        result = f"MemberAccess ({op_str}):\n"
        self.indent_level += 1

        result += self.get_indent() + "Object:\n"
        self.indent_level += 1
        result += self.get_indent() + node.object_.accept(self)
        self.indent_level -= 1

        result += self.get_indent() + f"Member: {node.member}\n"
        self.indent_level -= 1

        return result

    def visit_ArrayAccess(self, node):
        """Visit an array access expression"""
        result = "ArrayAccess:\n"
        self.indent_level += 1

        result += self.get_indent() + "Array:\n"
        self.indent_level += 1
        result += self.get_indent() + node.array.accept(self)
        self.indent_level -= 1

        result += self.get_indent() + "Index:\n"
        self.indent_level += 1
        result += self.get_indent() + node.index.accept(self)
        self.indent_level -= 2

        return result

    def visit_Statement(self, node):
        """Generic visit for Statement nodes"""
        return f"Statement: {type(node).__name__}\n"

    def visit_Expression(self, node):
        """Generic visit for Expression nodes"""
        return f"Expression: {type(node).__name__}\n"
