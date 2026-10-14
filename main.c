#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#define nybble char
#define byte unsigned char
#define word byte
#define pointer unsigned short
#define pointerOffset signed short

#define maxNybble 15
#define maxByte 255
#define maxPointer 65535
#define maxWord maxByte

#define getNybble(x) (x & maxNybble)
#define getByte(x) (x & maxByte)
#define getPointer(x) (x & maxPointer)
#define getWord(x) (x & maxWord)

#define castNybble(x) ((nybble)(x))
#define castByte(x) ((byte)(x))
#define castPointer(x) ((pointer)(x))
#define castWord(x) ((word)(x))

#define bytesToPointer(x, y) (((pointer)(x) << 8) | y)

#define state char
#define system 0
#define user 1

word regs[maxNybble+1];
word memoryLimitMin = 0;
word memoryLimitMax = 0;
pointer interruptResolverAddress = 0;
pointer syscallResolverAddress = 0;
pointer ip = 0;
pointer ir = 0;
state privilege = system;
bool zeroFlag = false;
bool carryFlag = false;
bool casFlag = false;
bool interruptsEnabled = false;
pointer interruptedIp = 0;
state interruptedPrivilege = system;
bool waitingForInterrupt = false;

bool shouldInterrupt = false;

typedef struct Device Device;
struct Device {
    void (*write)(Device*, pointer, word);
    word (*read)(Device*, pointer);
    byte* data;
    pointer size;
    pointer location;
};
Device* devices[256] = {0};

int deviceCount = 0;
void connectDevice(Device* device, pointer location) {
    device->location = location;
    devices[deviceCount++] = device;
}
Device *findDevice(pointer address) {
    for (int i = 0; i < deviceCount; i++) {
        Device *device = devices[i];
        if (address >= device->location && address < device->location + device->size)
            return device;
    }

    return NULL;
}

void printStatus() {
    printf("STATUS\n");

    printf("ip: %.4x\n", ip & maxPointer);
    printf("ir: %.4x\n", ir & maxPointer);
    printf("privilege: %d\n", privilege);
    printf("zeroFlag: %d\n", zeroFlag);
    printf("carryFlag: %d\n", carryFlag);
    printf("casFlag: %d\n", casFlag);
    printf("interruptedPc: %.4x\n", interruptedIp & maxPointer);
    printf("interruptedPrivilege: %d\n", interruptedPrivilege);

    printf("regs:\n");
    for (int i = 0; i < 16; i++) {
        printf("%.2x ", regs[i] & maxByte);
        if ((i & 7) == 7)
            printf("\n");
    }

    printf("\n");
}

word readRegs(nybble reg) {
    if ((reg >> 3) == 0 && privilege == user) {
        printf("ERROR:  Privileged register %d is trying to be read from in user mode at ip: %.4x.", reg, ip);
        exit(-1);
    }
    return regs[reg];
}

void writeRegs(nybble reg, word value) {
    if (reg >> 3 == 0 && privilege == user) {
        printf("ERROR:  Privileged register %d is trying to be written to in user mode at ip: %.4x.", reg, ip);
        exit(-1);
    }
    if (reg == 8) return;
    regs[reg] = value;
}

word read(pointer address) {
    if (((address >> 8) < regs[4] || (address >> 8) > regs[5]) && privilege == user) {
        printf("ERROR:  Address %.4x is trying to be read from in user mode at ip: %.4x.\nThis address is outside of the allowed pages %.2x - %.2x (inclusive)", address, ip, regs[4], regs[5]);
        exit(-1);
    }

    Device* device = findDevice(address);
    if (device != NULL)
        return device->read(device, address - device->location);

    return 0;
}

void write(pointer address, word value) {
    if (((address >> 8) < regs[4] || (address >> 8) > regs[5]) && privilege == user) {
        printf("ERROR:  Address %.4x is trying to be written to in user mode at ip: %.4x.\nThis address is outside of the allowed pages %.2x - %.2x (inclusive)", address, ip, regs[4], regs[5]);
        exit(-1);
    }
    Device* device = findDevice(address);
    if (device != NULL)
        device->write(device, address - device->location, value);
}

bool evalCond(nybble cond) {
    bool zero = zeroFlag && cond & 1;
    bool carry = carryFlag && cond & 2;
    bool cas = casFlag && cond & 4;

    bool output = zero || carry || cas;
    if (cond & 8) {
        return !output;
    }
    return output;
}

word performOperation(word valA, word valB, nybble operation) {
    short result;
    switch (operation) {
        case 0x0:
            result = valA + valB;
            break;
        case 0x1:
            result = valA + valB + carryFlag;
            break;
        case 0x2:
            result = valA + ~valB + 1;
            break;
        case 0x3:
            result = valA + ~valB + carryFlag;
            break;
        case 0x4:
            result = (valA + valB) >> 1;
            break;
        case 0x5:
            result = (valA + valB) >> 1;
            result |= (result & 0b01000000) << 1;
            break;
        case 0x6:
            result = valB;
            break;
        case 0x7:
            result = valA;
            break;
        case 0x8:
            result = valA & valB;
            break;
        case 0x9:
            result = valA | valB;
            break;
        case 0xA:
            result = valA ^ valB;
            break;
        case 0xB:
            result = (~valA) | valB;
            break;
        case 0xC:
            result = ~(valA & valB);
            break;
        case 0xD:
            result = ~(valA | valB);
            break;
        case 0xE:
            result = ~(valA ^ valB);
            break;
        case 0xF:
            result = ~((~valA) | valB);
            break;
        default:
            printf("WARN:   Operation '%x' is [reserved]", operation);
            result = valA + valB;
    }

    zeroFlag = false;
    carryFlag = false;
    if (result & 0x100) {
        carryFlag = true;
    }
    result = getWord(result);
    if (result == 0) {
        zeroFlag = true;
    }

    return result;
}

void cycle() {
    if (waitingForInterrupt) return;

    ir = (castPointer(read(ip)) << 8) | read(getPointer(ip + 1));

    nybble opcode = getNybble(ir >> 12);
    if ((opcode >> 3) == 0 && privilege == user) {
        printf("ERROR:  Privileged opcode %x is trying to be run in user mode at ip: %.4x.", opcode, ip);
        exit(-1);
    }

    ip += 2;

    nybble rd = getNybble(ir >> 8);
    nybble rs = getNybble(ir >> 4);
    nybble cond, operation, rt;
    cond = operation = rt = getNybble(ir);
    word immediate = (rs << 4) | cond;
    pointerOffset offset = cond << 12;
    offset >>= 12;

    pointer address;
    word valS, valD, valT, valRam;
    pointer SYS_HL = bytesToPointer(regs[6], regs[7]);
    pointer HL = bytesToPointer(regs[14], regs[15]) + bytesToPointer(memoryLimitMin, 0);
    if (privilege == system) HL = SYS_HL;
    switch (opcode) {
        // WFI
        case 0x0:
            waitingForInterrupt = true;
            break;
        // SRT
        case 0x1:
            ip = SYS_HL;
            privilege = user;
            break;
        // IST
        case 0x2:
            interruptsEnabled = rs & 1;
            break;
        // LMN
        case 0x3:
            memoryLimitMin = readRegs(rs);
            break;
        // LMX
        case 0x4:
            memoryLimitMax = readRegs(rs);
            break;
        // IRA
        case 0x5:
            interruptResolverAddress = SYS_HL;
            break;
        // SRA
        case 0x6:
            syscallResolverAddress = SYS_HL;
            break;
        // IRT
        case 0x7:
            ip = interruptedIp;
            privilege = interruptedPrivilege;
            break;
        // INM
        case 0x8:
            printf("INFO:   IMD (instructions modified) is not relevant for a single cycle uncached cpu.\n");
            break;
        // SCL
        case 0x9:
            writeRegs(6, ip >> 8);
            writeRegs(7, getByte(ip));
            ip = syscallResolverAddress;
            privilege = system;
            break;
        // LDI
        case 0xA:
            writeRegs(rd, immediate);
            break;
        // ALU
        case 0xB:
            valD = readRegs(rd);
            valS = readRegs(rs);
            word result = performOperation(valD, valS, operation);
            writeRegs(rd, result);
            break;
        // STR
        case 0xC:
            address = HL + offset;
            valS = readRegs(rs);
            write(address, valS);
            break;
        // LOD
        case 0xD:
            address = HL + offset;
            valRam = read(address);
            writeRegs(rd, valRam);
            break;
        // BAL
        case 0xE:
            if (evalCond(cond)) {
                pointer tmp = ip;
                ip = HL;
                HL = tmp - bytesToPointer(memoryLimitMin, 0);
                if (privilege == system) {
                    writeRegs(6, HL >> 8);
                    writeRegs(7, getByte(HL));
                } else {
                    writeRegs(14, HL >> 8);
                    writeRegs(15, getByte(HL));
                }
            }
            break;
        // CAS
        case 0xF:
            address = HL;
            valRam = read(address);
            valT = readRegs(rt);
            if (valRam == valT) {
                valS = readRegs(rs);
                write(address, valS);
                casFlag = true;
            } else {
                casFlag = false;
            }
            break;
        default:
            printf("Unimplemented opcode: %x\n", opcode);
            printStatus();
            exit(1);
    }
}

void causeInterrupt(word id) {
    printf("caused interrupt with id %d\n", id);

    shouldInterrupt = false;
    interruptedIp = ip;
    interruptedPrivilege = privilege;
    regs[0] = id;
    ip = interruptResolverAddress;
    waitingForInterrupt = false;
}

void loadBinary(const char* filePath, pointer address) {
    FILE *fptr = fopen(filePath, "rb");

    if (fptr == NULL) {
        printf("ERROR: Could not open file '%s'\n", filePath);
        return;
    }

    byte buffer[maxPointer];
    size_t bytesRead;
    pointer current = address;

    while ((bytesRead = fread(buffer, 1, sizeof(buffer), fptr)) > 0) {
        for (size_t i = 0; i < bytesRead; i++) {
            write(current++, buffer[i]);
        }
    }

    fclose(fptr);
}
/* --- END OF EMULATOR CODE --- */


#include "raylib.h"

const int pixelSize = 64;
const int screenWidthPixels = 16;
const int screenHeightPixels = 8;
const int screenWidth = screenWidthPixels * pixelSize;
const int screenHeight = screenHeightPixels * pixelSize;

const int terminalWidth = 16;
const int terminalHeight = 8;

void writeToRam(Device* self, pointer address, word value) {
    self->data[address] = value;
}
word readFromRam(Device* self, pointer address) {
    return self->data[address];
}

void writeToScreen(Device* self, pointer address, word value) {
    pointer x = address % screenWidthPixels;
    pointer y = address / screenWidthPixels;

    const Color colours[] = {BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, SKYBLUE, WHITE};

    SwapScreenBuffer();
    BeginDrawing();
    DrawRectangle(x*pixelSize, y*pixelSize, pixelSize, pixelSize, colours[value % 8]);
    EndDrawing();
}
word readFromScreen(Device* self, pointer address) {
    return 0;
}

void writeToTerminal(Device* self, pointer address, word value) {
    int x = address % terminalWidth;
    int y = address / terminalWidth;

    printf("\033[%d;%dH%c", y + 1, x + 1, value);
    fflush(stdout);
}
word readFromTerminal(Device* self, pointer address) {
    return 0;
}

int main(int argc, char* argv[]) {
    /* WINDOW */
    SetTraceLogLevel(LOG_ERROR);
    InitWindow(screenWidth, screenHeight, "Romulus Emulator");
    SetWindowState(FLAG_WINDOW_RESIZABLE);
    SetTargetFPS(60);

    BeginDrawing();
    ClearBackground(BLACK);
    EndDrawing();
    /* WINDOW */

    /* DEVICES */
    Device ram;
    byte ramData[0x8000] = {0};
    ram.write = writeToRam;
    ram.read = readFromRam;
    ram.data = ramData;
    ram.size = sizeof(ramData);
    connectDevice(&ram, 0x0000);

    Device screen;
    screen.write = writeToScreen;
    screen.read = readFromScreen;
    screen.data = NULL;
    screen.size = screenWidthPixels * screenHeightPixels;
    connectDevice(&screen, 0xFF80);

    Device terminal;
    terminal.write = writeToTerminal;
    terminal.read = readFromTerminal;
    terminal.data = NULL;
    terminal.size = terminalWidth * terminalHeight;
    connectDevice(&terminal, 0xFF00);
    /* DEVICES */


    loadBinary("z_binaries/printregister.bin", 0);


    while (!WindowShouldClose()) {
        cycle();
        PollInputEvents();
    }
    CloseWindow();


    return 0;
}