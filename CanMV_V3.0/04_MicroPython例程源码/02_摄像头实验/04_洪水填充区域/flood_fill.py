'''
本程序遵循GPL V3协议, 请遵循协议
实验平台: DshanPI CanMV
开发板文档站点	: https://eai.100ask.net/
百问网学习平台   : https://www.100ask.net
百问网官方B站    : https://space.bilibili.com/275908810
百问网官方淘宝   : https://100ask.taobao.com
'''
import time, os, gc, sys

from media.sensor import *
from media.display import *
from media.media import *

# 设置摄像头和图像处理的分辨率
DETECT_WIDTH = 480
DETECT_HEIGHT = 640

sensor = None

try:
    # 创建一个 Sensor 对象，使用默认配置，分辨率为 800x480
    sensor = Sensor(width=DETECT_WIDTH, height=DETECT_HEIGHT)

    # 重置传感器硬件（重新初始化）
    sensor.reset()

    # 如有需要可以打开水平翻转或垂直翻转（默认注释掉）
    # sensor.set_hmirror(False)
    # sensor.set_vflip(False)

    # 设置通道0输出图像的分辨率
    sensor.set_framesize(width=DETECT_WIDTH, height=DETECT_HEIGHT)

    # 设置图像格式为 RGB565（比 RGB888 更节省内存和带宽）
    sensor.set_pixformat(Sensor.RGB565)

    # 使用 LCD 屏作为图像输出（ST7701 是常见的 MIPI 屏控制器）
    Display.init(Display.ST7701, width=DETECT_WIDTH, height=DETECT_HEIGHT, to_ide=True)

    # 使用 IDE 虚拟显示器：
    # Display.init(Display.VIRT, width=DETECT_WIDTH, height=DETECT_HEIGHT, fps=100)

    # 初始化媒体缓冲管理器（内部用于图像传输和管理内存池）
    MediaManager.init()

    # 启动摄像头图像采集
    sensor.run()

    # 创建 FPS 统计对象
    fps = time.clock()

    while True:
        fps.tick()

        # 检查 IDE 是否发送退出命令
        os.exitpoint()

        # 捕获当前帧图像
        img = sensor.snapshot()

        # 设置泛洪填充的种子点坐标（图像中心）
        x = img.width() // 2
        y = img.height() // 2

        # 对种子点周围颜色相近区域进行填充：
        # - seed_threshold: 控制种子点颜色与周围像素的容差（0~1之间，越小越严格）
        # - floating_thresholds: 控制连通区域像素之间的容差
        # - color: 填充的颜色 (红色)
        # - invert: 是否对颜色条件取反（False 表示正常填充）
        # - clear_background: 是否将背景区域清除为黑色（False 表示保留）
        img.flood_fill(
            x, y,
            seed_threshold=0.05,
            floating_thresholds=0.05,
            color=(255, 0, 0),
            invert=False,
            clear_background=False
        )

        # 显示填充后的图像
        Display.show_image(img)

        # 主动释放垃圾回收资源（防止内存碎片或溢出）
        gc.collect()

        # 打印当前帧率（FPS）
        print(fps.fps())

except KeyboardInterrupt as e:
    print("用户中断程序")

except BaseException as e:
    print(f"运行异常：{e}")

finally:
    # 停止传感器
    if isinstance(sensor, Sensor):
        sensor.stop()

    # 释放显示设备资源
    Display.deinit()

    # 通知系统可进入休眠（用于嵌入式系统 IDE 停止）
    os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
    time.sleep_ms(100)

    # 释放媒体资源和内存
    MediaManager.deinit()
