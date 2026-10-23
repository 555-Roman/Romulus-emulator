from lexer_data import *


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.index = 0
        self.line = 0

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while self.index < len(self.text):
            char = self.text[self.index]

            match char:
                case "{":
                    tokens.append(Token(TokenType.OPEN_BRACE, char, self.line))
                case "}":
                    tokens.append(Token(TokenType.CLOSE_BRACE, char, self.line))
                case "(":
                    tokens.append(Token(TokenType.OPEN_PARENTHESIS, char, self.line))
                case ")":
                    tokens.append(Token(TokenType.CLOSE_PARENTHESIS, char, self.line))
                case ";":
                    tokens.append(Token(TokenType.SEMICOLON, char, self.line))
                case " ":
                    pass
                case "\t":
                    pass
                case "\n":
                    self.line += 1
                case _:
                    if char.isdigit():
                        integer_string = self.get_integer_string()
                        tokens.append(Token(TokenType.INTEGER_LITERAL, integer_string, self.line, int(integer_string)))
                    else:
                        if char.isalpha() or char == "_":
                            identifier = self.get_identifier()
                            if identifier in keywords:
                                tokens.append(Token(TokenType.KEYWORD, identifier, self.line))
                            else:
                                tokens.append(Token(TokenType.IDENTIFIER, identifier, self.line))
                        else:
                            print(f"Unrecognized character '{char}'")
                            exit(1)

            self.index += 1

        return tokens

    def get_integer_string(self) -> str:
        constructed_string = ""

        while self.index < len(self.text):
            char = self.text[self.index]
            if not char.isdigit():
                break
            constructed_string += char
            self.index += 1
        self.index -= 1

        return constructed_string

    def get_identifier(self) -> str:
        constructed_string = ""

        while self.index < len(self.text):
            char = self.text[self.index]
            if not (char.isalnum() or char == "_"):
                break
            constructed_string += char
            self.index += 1
        self.index -= 1

        return constructed_string


if __name__ == "__main__":
    file_path = input("What romulang file to tokenize: ")
    if file_path.endswith(".rml"): file_path = file_path[:-4]
    with open("z_romulang/" + file_path + ".rml", 'r') as assembly_file:
        global_text = "".join(assembly_file.readlines())
    global_tokens = Lexer(global_text).tokenize()
    print(global_tokens)
