'''
本程序遵循GPL V3协议, 请遵循协议
实验平台: DshanPI CanMV
开发板文档站点	: https://eai.100ask.net/
百问网学习平台   : https://www.100ask.net
百问网官方B站    : https://space.bilibili.com/275908810
百问网官方淘宝   : https://100ask.taobao.com
'''
import time, math, os, gc, sys

from media.sensor import *
from media.display import *
from media.media import *

# 定义一个函数，根据条形码类型返回相应的名称
def barcode_name(code):
    if(code.type() == image.EAN2):
        return "EAN2"
    if(code.type() == image.EAN5):
        return "EAN5"
    if(code.type() == image.EAN8):
        return "EAN8"
    if(code.type() == image.UPCE):
        return "UPCE"
    if(code.type() == image.ISBN10):
        return "ISBN10"
    if(code.type() == image.UPCA):
        return "UPCA"
    if(code.type() == image.EAN13):
        return "EAN13"
    if(code.type() == image.ISBN13):
        return "ISBN13"
    if(code.type() == image.I25):
        return "I25"
    if(code.type() == image.DATABAR):
        return "DATABAR"
    if(code.type() == image.DATABAR_EXP):
        return "DATABAR_EXP"
    if(code.type() == image.CODABAR):
        return "CODABAR"
    if(code.type() == image.CODE39):
        return "CODE39"
    if(code.type() == image.PDF417):
        return "PDF417"
    if(code.type() == image.CODE93):
        return "CODE93"
    if(code.type() == image.CODE128):
        return "CODE128"

# 定义检测图像的宽度和高度
DETECT_WIDTH = 640
DETECT_HEIGHT = 480

# 初始化传感器对象
sensor = None

try:
    # 使用默认配置构造一个传感器对象
    sensor = Sensor(width = DETECT_WIDTH, height = DETECT_HEIGHT)
    # 重置传感器
    sensor.reset()
    # 设置水平镜像（注释掉了，可根据需求启用）
    # sensor.set_hmirror(False)
    # 设置垂直翻转（注释掉了，可根据需求启用）
    # sensor.set_vflip(False)
    # 设置传感器的输出尺寸
    sensor.set_framesize(width = DETECT_WIDTH, height = DETECT_HEIGHT)
    # 设置传感器的输出格式为RGB565
    sensor.set_pixformat(Sensor.RGB565)

    # 使用LCD作为显示输出
    Display.init(Display.ST7701, width=DETECT_WIDTH, height=DETECT_HEIGHT, to_ide=True)

    # 初始化媒体管理器
    MediaManager.init()
    # 启动传感器开始运行
    sensor.run()

    # 使用时间模块记录帧率
    fps = time.clock()

    while True:
        # 更新帧率计数
        fps.tick()

        # 检查是否需要退出
        os.exitpoint()

        # 捕获一帧图像
        img = sensor.snapshot()

        # 查找图像中的所有条形码
        for code in img.find_barcodes():
            # 在条形码区域绘制矩形框，颜色为红色
            img.draw_rectangle([v for v in code.rect()], color=(255, 0, 0))

            # 打印条形码的详细信息
            print_args = (barcode_name(code), code.payload(), (180 * code.rotation()) / math.pi, code.quality(), fps.fps())
            print("条形码类型: %s, 有效载荷: \"%s\", 旋转角度: %f (度), 质量: %d, 帧率: %f" % print_args)

        # 将图像显示到屏幕上
        Display.show_image(img)

        # 执行垃圾回收
        gc.collect()

        # 打印当前的帧率
        print(fps.fps())
except KeyboardInterrupt as e:
    # 用户手动中断时输出提示
    print(f"用户停止")
except BaseException as e:
    # 捕获其他异常并打印异常信息
    print(f"异常 '{e}'")
finally:
    # 确保在退出时停止传感器
    if isinstance(sensor, Sensor):
        sensor.stop()

    # 关闭显示屏
    Display.deinit()

    # 启用休眠模式
    os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
    time.sleep_ms(100)

    # 释放媒体缓冲区
    MediaManager.deinit()
