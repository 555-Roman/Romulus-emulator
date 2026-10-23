from assembler import *
from code_generator import *


if __name__ == "__main__":
    file_path = input("What romulang file to compile: ")
    if file_path.endswith(".rml"): file_path = file_path[:-4]
    with open("z_romulang/" + file_path + ".rml", 'r') as romulang_file:
        global_text = "".join(romulang_file.readlines())

    global_tokens = Lexer(global_text).tokenize()
    global_ast = Parser(global_tokens).parse()
    global_assembly = CodeGenerator(global_ast).generate()
    global_binary = assemble(global_assembly)

    with open("z_binaries/" + file_path + ".bin", 'wb') as binary_file:
        binary_file.write(global_binary)