from parser import *


class CodeGenerator:
    def __init__(self, program: Program):
        self.program = program

    def generate(self) -> str:
        # TODO: remove after tests
        string = "#at 0x1000\n"
        return string + self.generate_function(self.program.function)

    def generate_function(self, function: Function) -> str:
        string = f".{function.name}:\n"
        return string + self.generate_statement(function.body)

    def generate_statement(self, statement: Statement) -> str:
        match statement:
            case Return():
                return f"\tLDI r9 {statement.expression.value}\n\tBAL true\n"
            case _:
                print(f"Unimplemented statement {type(statement)}.")
                exit(-1)


if __name__ == "__main__":
    file_path = input("What romulang file to compile: ")
    if file_path.endswith(".rml"): file_path = file_path[:-4]
    with open("z_romulang/" + file_path + ".rml", 'r') as romulang_file:
        global_text = "".join(romulang_file.readlines())
    global_tokens = Lexer(global_text).tokenize()
    global_ast = Parser(global_tokens).parse()
    global_assembly = CodeGenerator(global_ast).generate()
    print(global_assembly)
