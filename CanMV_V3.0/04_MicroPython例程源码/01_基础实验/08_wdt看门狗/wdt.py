'''
本程序遵循GPL V3协议, 请遵循协议
实验平台: DshanPI CanMV
开发板文档站点	: https://eai.100ask.net/
百问网学习平台   : https://www.100ask.net
百问网官方B站    : https://space.bilibili.com/275908810
百问网官方淘宝   : https://100ask.taobao.com
'''
from machine import WDT, Pin, FPIOA  # 导入模块
import time

# 映射 GPIO33 到普通 GPIO 功能
fpioa = FPIOA()
fpioa.set_function(33, FPIOA.GPIO33)

# 初始化 LED 引脚为输出
led = Pin(33, Pin.OUT)

# 构建看门狗对象，编号1，超时时间3秒
wdt = WDT(1, 3)

# 每隔1秒喂一次狗，执行3次
for i in range(3):
    time.sleep(1)
    print("喂狗次数:", i + 1)

    # 点亮 LED
    led.value(1)
    wdt.feed()  # 喂狗
    time.sleep(0.5)  # LED亮0.5秒
    led.value(0)  # 熄灭 LED

# 停止喂狗，系统会在3秒后自动复位
while True:
    time.sleep(0.5)
