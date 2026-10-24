from lexer import *


class ASTNode:
    pass

class Statement(ASTNode):
    pass

class Expression(ASTNode):
    pass


class Constant(Expression):
    def __init__(self, value: int):
        self.value = value

    def __repr__(self):
        return f"Constant({self.value})"

class UnaryOperation(Expression):
    def __init__(self, operator: Token, operand: Expression):
        self.operator = operator
        self.operand = operand

    def __repr__(self):
        return f"UnaryOperation({self.operator}{self.operand})"

class Return(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def __repr__(self):
        return f"Return({self.expression})"

class Function(ASTNode):
    def __init__(self, name: str, body: Statement):
        self.name = name
        self.body = body

    def __repr__(self):
        return f"Function({self.name}, {self.body})"

class Program(ASTNode):
    def __init__(self, function: Function):
        self.function = function

    def __repr__(self):
        return f"Program({self.function})"
