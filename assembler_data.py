string_escapes = {
    "n": "\n",
    "t": "\t",
    "r": "\r",
    "b": "\b",
    "f": "\f",
    "v": "\v",
    "0": "\0",
    "\\": "\\",
    "\"": "\"",
    "\'": "\'"
}

instructions = ["wfi", "srt", "ist", "lmn", "lmx", "ira", "sra", "irt",
                "inm", "scl", "ldi", "alu", "str", "lod", "bal", "cas"]
registers = ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7",
             "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]

word_registers = {"interrupt_id": 0,
                  "interruptid": 0,
                  "sys0": 1,
                  "sys1": 2,
                  "sys2": 3,
                  "sys3": 4,
                  "sys4": 5,
                  "sys5": 6,
                  "sys_h": 6,
                  "sysh": 6,
                  "sys6": 7,
                  "sys_l": 7,
                  "sysl": 7,
                  "zero": 8,
                  "r_zero": 8,
                  "rzero": 8,
                  "usr0": 8,
                  "usr1": 9,
                  "usr2": 10,
                  "usr3": 11,
                  "usr4": 12,
                  "usr5": 13,
                  "usr6": 14,
                  "usr_h": 14,
                  "usrh": 14,
                  "usr7": 15,
                  "usr_l": 15,
                  "usrl": 15,
                  "ra": 10,
                  "rb": 11,
                  "rc": 12,
                  "rd": 13,
                  "re": 14,
                  "rf": 15}
conditions = {"never": 0,
              "false": 0,
              "0": 1,
              "z": 1,
              "zero": 1,
              "e": 1,
              "eq": 1,
              "equal": 1,
              "=": 1,
              "==": 1,
              "c": 2,
              "carry": 2,
              "ge": 2,
              "greater_equal": 2,
              "greaterequal": 2,
              ">=": 2,
              "cas": 4,
              "compare_and_invert": 4,
              "compareandinvert": 4,
              "always": 8,
              "true": 8,
              "lt": 10,
              "less_than": 10,
              "lessthan": 10,
              "<": 10}
negations = ["!", "n", "not", "not_"]
operations = ["add", "adc", "sub", "sbb", "lrs", "ars", "mov", "cmp",
              "and", "ior", "xor", "imp", "nnd", "nor", "xnr", "nim"]
symbol_operations = {"+": 0,
                     "-": 2,
                     ">>": 4,
                     "&": 8,
                     "|": 9,
                     "^": 10}

no_operand = ["wfi", "srt", "ira", "sra", "irt", "inm", "scl"]
bool_only = ["ist"]
rd_only = ["lrs", "ars"]
rs_only = ["lmn", "lmx"]
cond_only = ["bal"]
rs_offset = ["str"]
rd_offset = ["lod"]
rs_rt = ["cas"]
rd_immediate = ["ldi"]
rd_rs_operation = ["alu"]
