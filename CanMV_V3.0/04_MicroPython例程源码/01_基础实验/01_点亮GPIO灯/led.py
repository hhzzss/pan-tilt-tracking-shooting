'''
本程序遵循GPL V3协议, 请遵循协议
实验平台: DshanPI CanMV
开发板文档站点	: https://eai.100ask.net/
百问网学习平台   : https://www.100ask.net
百问网官方B站    : https://space.bilibili.com/275908810
百问网官方淘宝   : https://100ask.taobao.com
'''
from machine import FPIOA, Pin
import time

# 实例化FPIOA
fpioa = FPIOA()
# 设置Pin33为GPIO33
fpioa.set_function(33, FPIOA.GPIO33)

# 实例化Pin33为输出
pin = Pin(33, Pin.OUT, pull=Pin.PULL_NONE, drive=7)

while True:
    pin.value(0)   # 点亮当前选择的LED
    time.sleep(0.5)  # 等待0.5秒
    pin.value(1)  # 熄灭当前选择的LED
    time.sleep(0.5)  # 等待0.5秒from machine import Pin
