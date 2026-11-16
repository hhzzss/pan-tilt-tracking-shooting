"""Run in CanMV IDE first; no camera or YOLO needed.

Default sends lost frames (no motion). Change MODE to "center" or
"direction" after checking stage 3 logs. Direction issues one 0.5s burst
then lost/quiet, and DOES NOT repeat; stage 4 can move the servos.
"""
from machine import UART, FPIOA
import time
from pantilt_uart import setup_uart, send_packet

MODE = "lost"  # lost / center / direction
AXIS = "yaw"  # yaw / pitch, used only by direction
ERROR = 150   # change to -150 to check the other direction

uart = setup_uart(UART, FPIOA())
try:
    if MODE not in ("lost", "center", "direction"):
        raise ValueError("unknown MODE")
    if MODE == "direction":
        if AXIS not in ("yaw", "pitch"):
            raise ValueError("unknown AXIS")
        # 10 frames at 20Hz, followed by explicit loss and 1s silence.
        for _ in range(10):
            send_packet(uart, True, ERROR if AXIS == "yaw" else 0,
                        ERROR if AXIS == "pitch" else 0)
            time.sleep_ms(50)
        send_packet(uart, False)
        time.sleep_ms(1000)
        print("direction test finished; servo must hold")
    else:
        while True:
            send_packet(uart, MODE == "center")
            time.sleep_ms(50)
finally:
    try:
        send_packet(uart, False)
    finally:
        uart.deinit()
