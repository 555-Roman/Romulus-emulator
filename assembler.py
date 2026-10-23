from assembler_data import *

def assemble(text: str, debug: bool = False) -> bytearray:
    file_tokens = []
    i = 0
    is_string = False
    string_delimiter = ""
    current_lexeme = ""
    current_line = []
    while i < len(text):
        char = text[i]
        if is_string:
            if char == "\\":
                i += 1
                if i >= len(text):
                    print("Unterminated string")
                    exit(1)
                escape = text[i]
                current_lexeme += string_escapes[escape]
            elif char == string_delimiter:
                is_string = False
                string_delimiter = ""
                current_lexeme += char
            else:
                current_lexeme += char
        else:
            if char in ["\"", "\'"]:
                is_string = True
                string_delimiter = char
                current_lexeme += char
            elif char in " \t":
                if current_lexeme.strip(" \t") != "":
                    if current_lexeme[0] not in ["'", '"']:
                        current_lexeme = current_lexeme.lower()
                    current_line.append(current_lexeme)
                    current_lexeme = ""
            elif char == "\n":
                if current_lexeme.strip(" \t") != "":
                    if current_lexeme[0] not in ["'", '"']:
                        current_lexeme = current_lexeme.lower()
                    current_line.append(current_lexeme)
                    current_lexeme = ""
                if current_line:
                    file_tokens.append(current_line)
                    current_line = []
            elif char == ";":
                while char != "\n":
                    i += 1
                    if i >= len(text):
                        break
                    char = text[i]
            else:
                current_lexeme += char
        i += 1

    if debug:
        print("FILE TOKENS:")
        print(file_tokens)
        print()

    labels = {}
    active_macros = {}
    ip = 0

    min_ip = 65535
    max_ip = 0

    ip_line_pair = []
    for i in range(len(file_tokens)):
        tokens = file_tokens[i]

        if len(tokens) == 0: continue
        if tokens[0] == ";": continue

        tokens = [active_macros[token] if token in active_macros.keys() else token for token in tokens]

        increment = 0
        if tokens[0] == "#define":
            active_macros[tokens[1]] = tokens[2]
        elif tokens[0] == "#undefine":
            active_macros.pop(tokens[1], None)
        elif tokens[0][0] == "." and tokens[0][-1] == ":":
            labels[tokens[0][:-1]] = ip
        elif tokens[0] == "#at":
            ip = int(tokens[1], 0)
        elif tokens[0] in instructions or tokens[0] in operations:
            increment = 2
        elif tokens[0] == "data":
            data = tokens[1]
            if len(data) >= 3 and data[0] == '"' and data[-1] == '"':
                increment = len(data) - 2
            elif len(data) >= 3 and data[0] == "'" and data[-1] == "'":
                increment = len(data) - 2
            else:
                try:
                    tmp = int(data, 0)
                    increment = tmp.bit_length() // 8 + 1
                except ValueError:
                    pass

        if increment != 0:
            ip_line_pair += [(ip, tokens)]
            min_ip = min(min_ip, ip)
            max_ip = max(max_ip, ip + increment)

        ip += increment
        ip = ip & 65535



    if debug:
        print("IP LINE PAIR:")
        print(ip_line_pair)
        print()
        print("LABELS:")
        print(labels)
        print()

    tmp = []
    for ip, tokens in ip_line_pair:
        tmp_tokens = []
        for token in tokens:
            if token in labels.keys():
                tmp_tokens += [str(labels[token] & 255)]
            elif token[:-2] in labels.keys():
                if token[-2:] == ".l":
                    tmp_tokens += [str(labels[token[:-2]] & 255)]
                elif token[-2:] == ".h":
                    tmp_tokens += [str((labels[token[:-2]] >> 8) & 255)]
                else:
                    print(f"ERROR:  Wrong suffix '{token[-2:]}' for label '{token[:-2]}'. Try '.l' or '.h'")
            else:
                tmp_tokens += [token]
        tmp += [(ip, tmp_tokens)]
    ip_line_pair = tmp

    if debug:
        print("IP LINE PAIR:")
        print(ip_line_pair)
        print()


    if debug:
        print("min ip:", min_ip)
        print("max ip:", max_ip)
        print()

    output = bytearray(max_ip - min_ip)

    def get_register_value(register_string: str) -> int:
        if register_string in registers:
            return registers.index(register_string)
        if register_string in word_registers.keys():
            return word_registers[register_string]

        print(f"ERROR:  unknown source register '{register_string}'")
        return 0
    def get_condition_value(condition_string: str) -> int:
        if condition_string in conditions.keys():
            return conditions[condition_string]
        for negation in negations:
            if condition_string.removesuffix(negation) in conditions.keys():
                return conditions[condition_string.removesuffix(negation)] + 8
        print(f"ERROR:  unknown condition '{condition_string}'")
        return 0
    def get_operation_value(operation_string: str) -> int:
        if operation_string in operations:
            return operations.index(operation_string)
        if operation_string in symbol_operations.keys():
            return symbol_operations[operation_string]
        print(f"ERROR:  unknown operation '{operation_string}'")
        return 0

    for ip, tokens in ip_line_pair:
        ip = ip - min_ip
        if tokens[0] == "data":
            data = tokens[1]
            if len(data) == 3 and data[0] == "'" and data[-1] == "'":
                output[ip] = ord(data[1])
            elif len(data) >= 3 and data[0] == '"' and data[-1] == '"':
                for char in data[1:-1]:
                    output[ip] = ord(char)
            else:
                value = int(data, 0)
                for i in range(value.bit_length() // 8):
                    output[ip] = (value >> (i * 8)) & 255
        elif tokens[0] in instructions:
            opcode = instructions.index(tokens[0])
            if tokens[0] in no_operand:
                output[ip] = opcode << 4
                output[ip+1] = 0
            elif tokens[0] in bool_only:
                value = int(tokens[1], 0) & 1
                output[ip] = opcode << 4
                output[ip+1] = value << 4
            elif tokens[0] in rs_only:
                rs = get_register_value(tokens[1])
                output[ip] = opcode << 4
                output[ip+1] = rs << 4
            elif tokens[0] in cond_only:
                condition = get_condition_value(tokens[1]) & 15
                output[ip] = (opcode << 4)
                output[ip+1] = condition
            elif tokens[0] in rs_offset:
                rs = get_register_value(tokens[1])
                try:
                    offset = int(tokens[2], 0) & 15
                except ValueError:
                    print("problem with offset:", tokens[2])
                    offset = 0
                output[ip] = opcode << 4
                output[ip+1] = (rs << 4) | offset
            elif tokens[0] in rd_offset:
                rd = get_register_value(tokens[1])
                try:
                    offset = int(tokens[2], 0) & 15
                except ValueError:
                    print("problem with offset:", tokens[2])
                    offset = 0
                output[ip] = (opcode << 4) | rd
                output[ip+1] = offset
            elif tokens[0] in rs_rt:
                rs = get_register_value(tokens[1])
                rt = get_register_value(tokens[2])
                output[ip] = (opcode << 4)
                output[ip+1] = (rs << 4) | rt
            elif tokens[0] in rd_immediate:
                rd = get_register_value(tokens[1])
                try:
                    immediate = int(tokens[2], 0) & 255
                except ValueError:
                    if len(tokens[2]) == 3 and tokens[2][0] == "'" and tokens[2][-1] == "'":
                        immediate = ord(tokens[2][1])
                    else:
                        print("problem with immediate:", tokens[2])
                        immediate = 0
                output[ip] = (opcode << 4) | rd
                output[ip+1] = immediate
            elif tokens[0] in rd_rs_operation:
                rd = get_register_value(tokens[1])
                rs = get_register_value(tokens[2])
                operation = get_operation_value(tokens[3])
                output[ip] = (opcode << 4) | rd
                output[ip+1] = (rs << 4) | operation
            else:
                print(f"ERROR:  what")
        elif tokens[0] in operations:
            opcode = instructions.index(rd_rs_operation[0])
            rd = get_register_value(tokens[1])
            if tokens[0] in rd_only:
                rs = 0
            else:
                rs = get_register_value(tokens[2])
            operation = get_operation_value(tokens[0])
            output[ip] = (opcode << 4) | rd
            output[ip+1] = (rs << 4) | operation
        else:
            print(f"ERROR:  what is '{tokens[0]}'?")

    if debug:
        print("MEMORY DUMP:")
        for address in range(min_ip // 16 * 16, (max_ip+2) // 16 * 16 + 16):
            if (address) % 16 == 0:
                string = hex(address)[2:].rjust(4, '0')
                print(string, end='    ')
            try:
                string = hex(output[address-min_ip])[2:].rjust(2, '0')
            except IndexError:
                string = "00"
            print(string, end=' ')
            if address % 16 == 15:
                print()

    return output

if __name__ == "__main__":
    file_path = input("What assembly file to assemble: ")
    if file_path.endswith(".asm"): file_path = file_path[:-4]
    with open("z_assembly/" + file_path + ".asm", 'r') as assembly_file:
        global_text = "".join(assembly_file.readlines())
    global_output = assemble(global_text)
    with open("z_binaries/" + file_path + ".bin", 'wb') as binary_file:
        binary_file.write(global_output)
