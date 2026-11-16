"""Disconnect C30D, then jumper K230 J6-2 TX to J6-3 RX. No main.py needed."""


def check_loopback(uart, clock):
    uart.read()  # Discard data left by a previous run.
    passed = 0
    for index in range(10):
        packet = ("K230-UART2-%02d\n" % index).encode("ascii")
        if uart.write(packet) != len(packet):
            raise OSError("UART write incomplete")
        received = b""
        start = clock.ticks_ms()
        while clock.ticks_diff(clock.ticks_ms(), start) < 300:
            data = uart.read()
            if data:
                received += data
                if len(received) >= len(packet):
                    break
            clock.sleep_ms(5)
        good = received == packet
        passed += int(good)
        print("%s %d/10 TX=%r RX=%r" %
              ("PASS" if good else "FAIL", index + 1, packet, received))
        clock.sleep_ms(100)
    print("RESULT: %d/10 matched" % passed)
    return passed


if __name__ == "__main__":
    from machine import UART, FPIOA
    import time

    fpioa = FPIOA()
    fpioa.set_function(44, fpioa.UART2_TXD)
    fpioa.set_function(45, fpioa.UART2_RXD)
    uart = UART(UART.UART2, baudrate=115200, bits=UART.EIGHTBITS,
                parity=UART.PARITY_NONE, stop=UART.STOPBITS_ONE)
    try:
        check_loopback(uart, time)
    finally:
        uart.deinit()
