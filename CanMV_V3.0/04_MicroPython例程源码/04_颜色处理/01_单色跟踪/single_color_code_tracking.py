'''
本程序遵循GPL V3协议, 请遵循协议
实验平台: DshanPI CanMV
开发板文档站点	: https://eai.100ask.net/
百问网学习平台   : https://www.100ask.net
百问网官方B站    : https://space.bilibili.com/275908810
百问网官方淘宝   : https://100ask.taobao.com
'''
import time, os, sys

from media.sensor import *  # 导入摄像头相关接口
from media.display import *  # 导入显示相关接口
from media.media import *  # 导入媒体资源相关接口

DETECT_WIDTH = 640  # 设置检测图像宽度
DETECT_HEIGHT = 480  # 设置检测图像高度

# 颜色识别阈值（L 最小值，L 最大值，A 最小值，A 最大值，B 最小值，B 最大值）
# 下面的阈值元组用于识别红色、绿色、蓝色。你可以根据需要调整这些阈值来改善识别效果。
thresholds = [
    (30, 100, 15, 127, 15, 127),  # 红色阈值
    (30, 100, -64, -8, 50, 70),   # 绿色阈值
    (0, 40, 0, 90, -128, -20)     # 蓝色阈值
]

sensor = None  # 摄像头对象

try:
    # 创建并初始化摄像头对象
    sensor = Sensor(width=DETECT_WIDTH, height=DETECT_HEIGHT)
    sensor.reset()  # 重置摄像头设置
    sensor.set_framesize(width=DETECT_WIDTH, height=DETECT_HEIGHT)  # 设置帧大小
    sensor.set_pixformat(Sensor.RGB565)  # 设置图像格式为 RGB565

    # 初始化显示设备，使用 LCD 显示器
    Display.init(Display.ST7701, width=DETECT_WIDTH, height=DETECT_HEIGHT, to_ide=True)

    # 初始化媒体资源管理器
    MediaManager.init()

    # 启动摄像头采集
    sensor.run()

    # 初始化帧率计时器
    clock = time.clock()

    while True:
        clock.tick()  # 每帧开始时计时

        # 获取当前图像帧
        img = sensor.snapshot()

        # 查找符合颜色阈值的 blobs，分别检测红色、绿色和蓝色
        blobs = img.find_blobs([thresholds[0], thresholds[1], thresholds[2]])
        #blobs = img.find_blobs([thresholds[0]]) #检测红色
        #blobs = img.find_blobs([thresholds[1]]) #检测绿色
        #blobs = img.find_blobs([thresholds[2]]) #检测蓝色

        # 如果检测到 blobs，绘制矩形和交叉线标记
        if blobs:
            for b in blobs:
                img.draw_rectangle(b[0:4], thickness=4)  # 绘制矩形框
                img.draw_cross(b[5], b[6], thickness=2)  # 绘制交叉线标记

        # 在图像左上角显示 FPS
        img.draw_string_advanced(0, 0, 30, 'FPS: ' + str("%.3f" % (clock.fps())), color=(255, 255, 255))

        # 显示图像到屏幕
        Display.show_image(img)

        # 打印当前 FPS
        print(clock.fps())

except KeyboardInterrupt as e:
    print(f"用户停止")
except BaseException as e:
    print(f"异常发生：'{e}'")
finally:
    # 停止摄像头采集
    if isinstance(sensor, Sensor):
        sensor.stop()

    # 关闭显示
    Display.deinit()

    # 释放媒体资源
    MediaManager.deinit()
