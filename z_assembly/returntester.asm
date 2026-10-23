#define x r9
#define charachterOffset r11
#define digit r12
#define checker r13
#define tmp r14
#define one r15
#define terminalPositionH r4
#define terminalPositionL r5


ldi sysH .program.h
ldi sysL .program.l
bal true


ldi terminalPositionH .terminal.h
ldi terminalPositionL .terminal.l

.print_r9:
    ldi charachterOffset '0'
    ldi one 1

    ldi checker 100
    ldi digit 0
    .hundredths:
        ldi sysH .endOfHundredths.h
        ldi sysL .endOfHundredths.l
        mov tmp x
        sub tmp checker
        bal carry
        mov x tmp
        add digit one
        ldi sysH .hundredths.h
        ldi sysL .hundredths.l
        bal true
    .endOfHundredths:
    mov sysL terminalPositionL
    mov sysH terminalPositionH
    add terminalPositionL one
    adc terminalPositionH r8
    add digit charachterOffset
    str digit 0

    ldi checker 10
    ldi digit 0
    .tens:
        mov tmp x
        sub tmp checker
        ldi sysH .endOfTens.h
        ldi sysL .endOfTens.l
        bal carry
        mov x tmp
        add digit one
        ldi sysH .tens.h
        ldi sysL .tens.l
        bal true
    .endOfTens:
    mov sysL terminalPositionL
    mov sysH terminalPositionH
    add terminalPositionL one
    adc terminalPositionH r8
    add digit charachterOffset
    str digit 0

    .ones:
    mov sysL terminalPositionL
    mov sysH terminalPositionH
    add terminalPositionL one
    adc terminalPositionH r8
    add x charachterOffset
    str x 0

#at 0x1000
.program:


#at 0xFF00
.terminal:
