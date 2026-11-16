'''
本程序遵循GPL V3协议, 请遵循协议
实验平台: DshanPI CanMV
开发板文档站点	: https://eai.100ask.net/
百问网学习平台   : https://www.100ask.net
百问网官方B站    : https://space.bilibili.com/275908810
百问网官方淘宝   : https://100ask.taobao.com
'''
from machine import TOUCH
import time

# 创建 TOUCH 类的实例，使用设备号 0
touch_panel = TOUCH(0)

# 每次最多打印的触摸点数（通常触摸屏最多支持 5 点触控）
MAX_TOUCH_POINTS = 5

while True:
    # 读取触摸数据（返回元组，包含多个触点）
    touch_points = touch_panel.read()

    if touch_points:
        print("检测到触摸事件")

        # 遍历每个触摸点，仅打印坐标信息
        for point in touch_points[:MAX_TOUCH_POINTS]:
            print("x = {}, y = {}".format(point.x, point.y))

    time.sleep_ms(50)
