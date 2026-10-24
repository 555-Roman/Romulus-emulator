from parser import *


class CodeGenerator:
    def __init__(self, program: Program):
        self.program = program
        self.label_index = -1

    def generate(self) -> str:
        # TODO: remove after tests
        tmp = "#at 0x1000\n"
        return tmp + self.generate_function(self.program.function)

    def generate_function(self, function: Function) -> str:
        function_label = f".{function.name}:\n"
        save_return_address = "\tMOV r14 sysH\n\tMOV r15 sysL\n"
        return function_label + save_return_address + self.generate_statement(function.body)

    def generate_statement(self, statement: Statement) -> str:
        match statement:
            case Return():
                expression = self.generate_expression(statement.expression)
                restore_return_address = "\tMOV sysH r14\n\tMOV sysL r15\n"
                return expression + restore_return_address + "\tBAL true\n"
            case _:
                print(f"Unimplemented statement {type(statement)}.")
                exit(-1)

    def generate_expression(self, expression: Expression) -> str:
        match expression:
            case Constant():
                return f"\tLDI r9 {expression.value}\n"
            case UnaryOperation():
                subexpression = self.generate_expression(expression.operand)
                match expression.operator.token_type:
                    case TokenType.BITWISE_NOT:
                        return subexpression + "\tXNOR r9 r8\n"
                    case TokenType.MINUS:
                        return subexpression + "\tMOV r10 r9\n\tLDI r9 0\n\tSUB r9 r10\n"
                    case TokenType.LOGICAL_NOT:
                        label = self.get_label()
                        return subexpression + f"\tCMP r9 r8\n\tLDI r9 0\n\tLDI sysH {label}.h\n\tLDI sysL {label}.l\n\tBAL not_equal\n\tLDI r9 1\n{label}:\n"
                    case _:
                        print(f"Unimplemented {expression.operator.token_type}")
                        exit(-1)
            case _:
                print(f"Unimplemented expression {type(expression)}.")
                exit(-1)

    def get_label(self) -> str:
        self.label_index += 1
        return f".label{self.label_index}"


if __name__ == "__main__":
    file_path = input("What romulang file to compile: ")
    if file_path.endswith(".rml"): file_path = file_path[:-4]
    with open("z_romulang/" + file_path + ".rml", 'r') as romulang_file:
        global_text = "".join(romulang_file.readlines())
    global_tokens = Lexer(global_text).tokenize()
    global_ast = Parser(global_tokens).parse()
    global_assembly = CodeGenerator(global_ast).generate()
    print(global_assembly)
