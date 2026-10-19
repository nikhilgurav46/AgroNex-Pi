#!/usr/bin/env python3
"""
AgroNex: Raw QMC5883P (HW-127) I2C Diagnostic
Reads directly from I2C bus without going through hardware.py,
dumps raw register bytes and computed heading so we can debug the chip.
Run on the Pi:  python3 test_compass_raw.py
"""
import time
import math
import sys

try:
    from smbus2 import SMBus
except ImportError:
    print("ERROR: smbus2 not installed. Run: pip install smbus2")
    sys.exit(1)

ADDR = 0x2C   # QMC5883P address confirmed by i2cdetect
BUS  = 1      # I2C bus 1 on RPi 4

def signed_le(lsb, msb):
    v = (msb << 8) | lsb
    return v - 65536 if v >= 32768 else v

def init_chip(bus):
    print(f"Soft-resetting QMC5883P at 0x{ADDR:02X}...")
    bus.write_byte_data(ADDR, 0x0A, 0x80)   # Soft reset
    time.sleep(0.05)
    bus.write_byte_data(ADDR, 0x0B, 0x01)   # Set/Reset period
    # Control reg 0x09:
    #   OSR=11 (512)  => bits [7:6] = 11
    #   RNG=01 (8G)   => bits [5:4] = 01
    #   ODR=10 (50Hz) => bits [3:2] = 10  (50Hz for reliable DRDY)
    #   MODE=01       => bits [1:0] = 01 (continuous)
    # => 0b11_01_10_01 = 0xD9
    bus.write_byte_data(ADDR, 0x09, 0xD9)
    time.sleep(0.1)
    print("Init complete. Control reg 0x09 = 0xD9 (Continuous, 50Hz, 8G, OSR512)")

def wait_drdy(bus, timeout=0.5):
    deadline = time.time() + timeout
    polls = 0
    while time.time() < deadline:
        status = bus.read_byte_data(ADDR, 0x06)
        polls += 1
        if status & 0x01:
            return True, polls, status
        time.sleep(0.005)
    status = bus.read_byte_data(ADDR, 0x06)
    return False, polls, status

def read_raw(bus):
    data = bus.read_i2c_block_data(ADDR, 0x00, 7)  # 6 data + 1 status
    x = signed_le(data[0], data[1])
    y = signed_le(data[2], data[3])
    z = signed_le(data[4], data[5])
    status = data[6]
    return x, y, z, status, data

def main():
    print("="*60)
    print("  AgroNex: QMC5883P (HW-127) Raw Compass Diagnostic")
    print("="*60)
    print(f"  I2C Bus: {BUS}, Address: 0x{ADDR:02X}")
    print("="*60)

    bus = SMBus(BUS)

    # Scan for device presence
    try:
        _ = bus.read_byte(ADDR)
        print(f"OK Device found at 0x{ADDR:02X}")
    except Exception as e:
        print(f"FAIL No device at 0x{ADDR:02X}: {e}")
        sys.exit(1)

    # Read chip ID registers
    try:
        chip_id = bus.read_byte_data(ADDR, 0x0D)
        print(f"   Chip ID reg (0x0D) = 0x{chip_id:02X}  (QMC5883L/P expect 0xFF)")
        chip_id_alt = bus.read_byte_data(ADDR, 0x0C)
        print(f"   Chip ID reg (0x0C) = 0x{chip_id_alt:02X}  (QMC5883P expect 0x1B)")
    except Exception as e:
        print(f"   Could not read chip ID: {e}")

    try:
        init_chip(bus)
    except Exception as e:
        print(f"FAIL Init failed: {e}")
        sys.exit(1)

    print("\nReading 20 samples — SLOWLY ROTATE the compass module while running:\n")
    print(f"{'#':>4}  {'X':>7} {'Y':>7} {'Z':>7}  {'StatusByte':>12}  {'DRDY':>7}  {'Heading':>9}")
    print("-"*70)

    DECLINATION = 0.0  # Change to your local declination if needed

    for i in range(1, 21):
        ready, polls, status_byte = wait_drdy(bus, timeout=0.5)
        x, y, z, status, raw_bytes = read_raw(bus)
        raw_hex = " ".join(f"{b:02X}" for b in raw_bytes)

        if x == 0 and y == 0 and z == 0:
            heading_str = "  ZERO DATA"
        elif x == -4096 or y == -4096:
            heading_str = "  OVERFLOW "
        else:
            h = (math.degrees(math.atan2(y, x)) + DECLINATION) % 360.0
            heading_str = f"{h:8.1f}deg"

        drdy_str = "READY" if ready else "TIMEOUT"
        print(f"[{i:02d}]  {x:7d} {y:7d} {z:7d}  0x{status_byte:02X}({status_byte:08b})  {drdy_str:>7}  {heading_str}")
        print(f"       Raw bytes: {raw_hex}")
        time.sleep(0.3)

    bus.close()
    print("\nDone.")
    print("If heading changes as you rotate: compass is working correctly.")
    print("If X=0 Y=0 Z=0 every time:       check VCC/GND/SDA/SCL wiring.")

if __name__ == "__main__":
    main()
