'''
  Copyright (C) 2008-2023 深圳百问网科技有限公司
  All rights reserved

 免责声明: 百问网编写的程序, 用于商业用途请遵循GPL许可, 百问网不承担任何后果！

 本程序遵循GPL V3协议, 请遵循协议
 百问网学习平台   : https://www.100ask.net
 百问网交流社区   : https://forums.100ask.net
 百问网官方B站    : https://space.bilibili.com/275908810
 本程序所用开发板 : DshanPI-CanMV开发板
 开发板文档站点	： https://eai.100ask.net/
 百问网官方淘宝   : https://100ask.taobao.com
 联系我们(E-mail) : weidongshan@100ask.net
'''
from machine import Pin, FPIOA, Timer
import time

# ========== FPIOA 映射 ==========
fpioa = FPIOA()

# LED 引脚（物理引脚号）
led_pin = 33

# 将物理引脚映射到同号的 GPIO 功能
fpioa.set_function(led_pin, FPIOA.GPIO33)

# ========== 初始化 LED 引脚为输出模式 ==========
led = Pin(led_pin, Pin.OUT, pull=Pin.PULL_NONE, drive=7)
led.value(0)      # 初始熄灭（低电平点亮，若高电平点亮请改为 1）

# ========== 定时器回调函数：点亮 LED ==========
def turn_on_led(t):
    led.value(1)      # 点亮 LED
    print("LED 已点亮（定时器触发）")

# ========== 创建定时器并设置为单次模式 ==========
tim = Timer(-1)               # 创建一个软件定时器
tim.init(period=1000, mode=Timer.ONE_SHOT, callback=turn_on_led)   # 延时 1000ms 后点亮

print("定时器已启动，1 秒后将点亮 LED...")

# ========== 主线程：保持运行一段时间，然后停止定时器 ==========
time.sleep(2)                 # 等待定时器执行完毕
tim.deinit()                  # 停止定时器（可选）
print("定时器已释放，LED 保持点亮状态")
