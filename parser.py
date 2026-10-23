from lexer import *
from parser_data import *


def parsing_error(*args):
    print(*args)
    exit(1)

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0

    def parse(self) -> Program:
        function = self.parse_function()
        if self.index < len(self.tokens):
            parsing_error(f"Unexpected token {self.tokens[self.index]} after function definition.")
        return Program(function)

    def parse_function(self) -> Function:
        self.expect_keyword("u8")
        name = self.expect(TokenType.IDENTIFIER).lexeme
        self.expect(TokenType.OPEN_PARENTHESIS)
        self.expect(TokenType.CLOSE_PARENTHESIS)
        self.expect(TokenType.OPEN_BRACE)
        statement = self.parse_statement()
        self.expect(TokenType.CLOSE_BRACE)
        return Function(name, statement)

    def parse_statement(self) -> Statement:
        self.expect_keyword("return")
        expression = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        return Return(expression)

    def parse_expression(self) -> Expression:
        return self.parse_constant()

    def parse_constant(self) -> Constant:
        token = self.expect(TokenType.INTEGER_LITERAL)
        return Constant(token.value)

    def expect(self, token_type: TokenType) -> Token:
        if self.index >= len(self.tokens):
            parsing_error(f"Expected tokens of type {token_type.name} but reached end of file.")
        token = self.tokens[self.index]
        if token.token_type != token_type:
            parsing_error(f"Expected token of type {token_type.name} but got {token.token_type.name}.")
        self.index += 1
        return token

    def expect_keyword(self, keyword: str) -> Token:
        token = self.expect(TokenType.KEYWORD)
        if token.lexeme != keyword:
            parsing_error(f"Expected keyword {keyword} but got {token.lexeme}.")
        return token


if __name__ == "__main__":
    file_path = input("What romulang file to parse: ")
    if file_path.endswith(".rml"): file_path = file_path[:-4]
    with open("z_romulang/" + file_path + ".rml", 'r') as assembly_file:
        global_text = "".join(assembly_file.readlines())
    global_tokens = Lexer(global_text).tokenize()
    global_ast = Parser(global_tokens).parse()
    print(global_ast)
