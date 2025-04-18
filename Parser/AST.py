class ASTNode:
    """
    Base class for all AST nodes.
    Provides a method for accepting visitors.
    """

    def accept(self, visitor):
        method = getattr(visitor, f"visit_{self.__class__.__name__}")
        return method(self)


class Program(ASTNode):
    """
    Represents the root of the AST, containing a list of statements.
    """

    def __init__(self, body=None):
        self.body = body  # List of statements


class Statement(ASTNode):
    """
    Base class for all statements.
    """

    pass


class VarDecl(Statement):
    """
    Represents a variable declaration (let/const).
    """

    def __init__(self, decl_statement, identifier, value):
        self.decl_statement = decl_statement  # 'const' or 'let'
        self.identifier = identifier  # Variable name
        self.value = value  # Expression assigned to the variable


class TypeDecl(Statement):
    """
    Represents a type declaration (e.g., struct).
    """

    def __init__(self, identifier, fields):
        self.identifier = identifier  # Name of the type
        self.fields = fields  # List of Field objects


class Field(ASTNode):
    """
    Represents a field in a type declaration.
    """

    def __init__(self, identifier, type_):
        self.identifier = identifier  # Field name
        self.type_ = type_  # Type of the field


class FunDecl(Statement):
    """
    Represents a function declaration.
    """

    def __init__(self, identifier, params, body, return_type=None):
        self.identifier = identifier  # Function name
        self.params = params  # List of Param objects
        self.return_type = return_type  # Return type (optional)
        self.body = body  # Function body (Block)


class Param(ASTNode):
    """
    Represents a parameter in a function declaration.
    """

    def __init__(self, identifier, type_):
        self.identifier = identifier  # Parameter name
        self.type_ = type_  # Type of the parameter


class Block(ASTNode):
    """
    Represents a block of statements enclosed in braces.
    """

    def __init__(self, statements):
        self.statements = statements  # List of statements


class IfStmt(Statement):
    """
    Represents an if statement, with optional else or else-if blocks.
    """

    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition  # Condition expression
        self.then_block = then_block  # Block executed if condition is true
        self.else_block = else_block  # Block executed if condition is false (optional)


class LoopStmt(Statement):
    """
    Represents a loop statement (while, for, repeat).
    """

    def __init__(self, loop_type, condition, body):
        self.loop_type = loop_type  # Type of loop ('while', 'for', 'repeat')
        self.condition = condition  # Loop condition
        self.body = body  # Loop body (Block)


class Expression(ASTNode):
    """
    Base class for all expressions.
    """

    pass


class BinaryOp(Expression):
    """
    Represents a binary operation (e.g., +, -, &&, ||).
    """

    def __init__(self, lhs, op, rhs):
        self.lhs = lhs  # Left-hand side expression
        self.op = op  # Operator (e.g., '+', '-', '&&', etc.)
        self.rhs = rhs  # Right-hand side expression


class UnaryOp(Expression):
    """
    Represents a unary operation (e.g., -, !).
    """

    def __init__(self, operator, operand):
        self.operator = operator  # Operator (e.g., '-', '!')
        self.operand = operand  # Operand expression


class Literal(Expression):
    """
    Represents a literal value (e.g., number, string, boolean).
    """

    def __init__(self, value):
        self.value = value  # Literal value


class Identifier(Expression):
    """
    Represents an identifier (e.g., variable or function name).
    """

    def __init__(self, name):
        self.name = name  # Name of the identifier


class Call(Expression):
    """
    Represents a function call.
    """

    def __init__(self, callee, arguments):
        self.callee = callee  # Expression representing the function being called
        self.arguments = arguments  # List of argument expressions


class MemberAccess(Expression):
    """
    Represents member access (e.g., object.member or object?.member).
    """

    def __init__(self, object_, member, op):
        self.object_ = object_  # Expression representing the object
        self.member = member  # Name of the member being accessed
        self.op = op  # Operator ('.' or '?.')


class ArrayAccess(Expression):
    """
    Represents array access (e.g., array[index]).
    """

    def __init__(self, array, index):
        self.array = array  # Expression representing the array
        self.index = index  # Expression representing the index
