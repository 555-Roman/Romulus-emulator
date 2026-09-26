#define screenBase 0xFF80
#define black 0b000
#define red 0b001
#define green 0b010
#define yellow 0b011
#define blue 0b100
#define magenta 0b101
#define cyan 0b110
#define white 0b111

ldi sys_h .screenBase.h
ldi sys_l .screenBase.l
ldi r9 green
sta r9 0
ldi r9 blue
sta r9 1
wfi;   test

#at 0x100
.string:
data "Hello, World!\0"
.char:
data '\n'
.32b_int:
data 0xdeadbeef

#at screenBase
.screenBase:
;data 0x06
;data 0x06
;data 0x06