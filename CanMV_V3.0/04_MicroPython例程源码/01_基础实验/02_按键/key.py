'''
本程序遵循GPL V3协议, 请遵循协议
实验平台: DshanPI CanMV
开发板文档站点	: https://eai.100ask.net/
百问网学习平台   : https://www.100ask.net
百问网官方B站    : https://space.bilibili.com/275908810
百问网官方淘宝   : https://100ask.taobao.com
'''
from machine import Pin, FPIOA
import time

# 初始化 FPIOA 并映射功能
fpioa = FPIOA()
fpioa.set_function(33, FPIOA.GPIO33)  # LED 接在 GPIO33

# 四个按键对应的GPIO
key_pins = [14, 18, 27, 29]
for pin in key_pins:
    fpioa.set_function(pin, getattr(FPIOA, f'GPIO{pin}'))

# 初始化设备
led = Pin(33, Pin.OUT)                    # LED 输出控制
led.value(0)                              # 初始状态熄灭

# 初始化四个按键，上拉输入
keys = []
for pin in key_pins:
    keys.append(Pin(pin, Pin.IN, Pin.PULL_UP))

while True:
    led_on = False  # 标记是否有按键按下

    # 循环检测四个按键
    for i, key in enumerate(keys):
        if key.value() == 0:  # 检测到按键按下（低电平）
            time.sleep_ms(10)  # 消抖延时
            if key.value() == 0:  # 确认按键确实按下
                led.value(1)  # 点亮LED
                print(f"按键 IO{key_pins[i]} 按下，灯亮")
                led_on = True

                # 等待按键松开
                while key.value() == 0:
                    pass

                print(f"按键 IO{key_pins[i]} 松开，灯灭")
                led.value(0)  # 按键松开后立即熄灭LED
                break  # 退出当前按键检测，重新开始循环

    # 如果没有按键按下，确保LED熄灭
    if not led_on:
        led.value(0)

    time.sleep_ms(10)  # 小延时避免CPU占用过高
