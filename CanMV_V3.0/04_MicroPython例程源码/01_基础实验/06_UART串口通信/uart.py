'''
本程序遵循GPL V3协议, 请遵循协议
实验平台: DshanPI CanMV
开发板文档站点	: https://eai.100ask.net/
百问网学习平台   : https://www.100ask.net
百问网官方B站    : https://space.bilibili.com/275908810
百问网官方淘宝   : https://100ask.taobao.com
'''
from machine import UART
from machine import FPIOA
import time

# 实例化FPIOA
from machine import FPIOA
fpioa = FPIOA()
#设置pin44为串口2发送管脚
fpioa.set_function(44, fpioa.UART2_TXD)
#设置pin45为串口2接收管脚
fpioa.set_function(45, fpioa.UART2_RXD)

#UART: baudrate 115200, 8bits, parity none, one stopbits
uart = UART(UART.UART2, baudrate=115200, bits=UART.EIGHTBITS, parity=UART.PARITY_NONE, stop=UART.STOPBITS_ONE)
#打印串口配置
print(uart)
# UART write
r = uart.write("Hello 100ASK UART test")
print(r)
# UART read
r = uart.read()
print(r)
# UART readline
r = uart.readline()
print(r)
# UART readinto
b = bytearray(8)
r = uart.readinto(b)
print(r)

while True:
    t = uart.read()
    if t != None:
        print(t)
    time.sleep(0.1)

