; ptr string = .string;
; ptr terminal = 0xFF00;
; var i = 0;
; loop {
;   var char = *string;
;   if (char == "\0") {
;     break;
;   }
;   *terminal = char;
;   string++;
;   terminal++;
; }

#define stringH r14
#define stringL r15
#define terminalH r12
#define terminalL r13
#define i r9
#define char r10

; init
ldi stringH .string.h
ldi stringL .string.l
ldi terminalH .terminal.h
ldi terminalL .terminal.l
ldi i 0
; start of loop
.loop:
    ; char = *string
    mov sysH stringH
    mov sysL stringL
    lod char 0
    ; if (char == 0) {break;}
    ldi sysH .endOfLoop.h
    ldi sysL .endOfLoop.l
    cmp char r8
    bal equal
    ; *terminal = char;
    mov sysH terminalH
    mov sysL terminalL
    str char 0
    ; string++;
    ldi r11 1
    add stringL r11
    adc stringH r8
    ; terminal++;
    ldi r11 1
    add terminalL r11
    adc terminalH r8
    ; branch back
    ldi sysH .loop.h
    ldi sysL .loop.l
    bal true
; end of loop
.endOfLoop:
wfi

.string:
data "Hello, World!"
data 0

#at 0xFF00
.terminal:
