from machine import UART, FPIOA
import time

# K230 J6-2：IO44，连接C30D蓝牙接口D6
# K230 J6-4：GND，连接C30D的G
fpioa = FPIOA()
fpioa.set_function(44, FPIOA.UART2_TXD)
fpioa.set_function(45, FPIOA.UART2_RXD)

uart = UART(
    UART.UART2,
    baudrate=115200,
    bits=UART.EIGHTBITS,
    parity=UART.PARITY_NONE,
    stop=UART.STOPBITS_ONE
)

count = 0
try:
    while True:
        packet = b"$T,0,0,0\n"
        if uart.write(packet) != len(packet):
            raise OSError("UART发送不完整")

        count += 1
        if count % 20 == 0:
            print("已发送帧数：", count)

        time.sleep_ms(50)
finally:
    uart.deinit()
