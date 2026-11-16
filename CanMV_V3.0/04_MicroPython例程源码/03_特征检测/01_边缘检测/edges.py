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

# 设置图像采集和处理的分辨率（宽度按16对齐）
DETECT_WIDTH = ALIGN_UP(480, 16)
DETECT_HEIGHT = 640

sensor = None

# 摄像头初始化函数
def camera_init():
    global sensor

    # 创建传感器对象，指定采集分辨率
    sensor = Sensor(width=DETECT_WIDTH, height=DETECT_HEIGHT)

    # 重置传感器硬件
    sensor.reset()

    # 可选：水平镜像开关
    # sensor.set_hmirror(False)

    # 可选：垂直翻转开关
    # sensor.set_vflip(False)

    # 设置输出分辨率
    sensor.set_framesize(width=DETECT_WIDTH, height=DETECT_HEIGHT)

    # 设置图像格式为灰度图（适合边缘检测）
    sensor.set_pixformat(Sensor.GRAYSCALE)

    # 使用虚拟显示器（也会输出到 IDE）
    Display.init(Display.ST7701, width=DETECT_WIDTH, height=DETECT_HEIGHT, fps=60, to_ide=True)

    # 初始化媒体缓冲池管理器
    MediaManager.init()

    # 启动图像采集
    sensor.run()

# 摄像头释放函数
def camera_deinit():
    global sensor

    # 停止图像采集
    sensor.stop()

    # 释放显示设备
    Display.deinit()

    # 通知 IDE 可以进入休眠状态
    os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
    time.sleep_ms(100)

    # 释放媒体缓冲区资源
    MediaManager.deinit()

# 图像采集和处理主循环
def capture_picture():
    # 创建 FPS 计时器对象
    fps = time.clock()

    while True:
        fps.tick()

        try:
            # IDE 控制点检查，支持在 IDE 中点击停止运行
            os.exitpoint()

            global sensor

            # 获取一帧图像（灰度图）
            dect_img = sensor.snapshot()

            # 使用 Canny 算法进行边缘检测
            dect_img.find_edges(image.EDGE_CANNY, threshold=(50, 80))

            # 可选：使用简单边缘检测算法（效率更高，效果略差）
            # dect_img.find_edges(image.EDGE_SIMPLE, threshold=(100, 255))

            # 将结果图像显示到 IDE 或屏幕上
            Display.show_image(dect_img)

            # 释放图像对象，便于垃圾回收
            del dect_img
            gc.collect()

            # 打印当前帧率
            print(fps.fps())

        except KeyboardInterrupt as e:
            print("用户中断运行：", e)
            break
        except BaseException as e:
            print(f"运行异常：{e}")
            break

# 主程序入口
def main():
    # 启用 IDE 控制点（允许 IDE 退出控制）
    os.exitpoint(os.EXITPOINT_ENABLE)

    camera_is_init = False

    try:
        print("摄像头初始化")
        camera_init()
        camera_is_init = True

        print("开始图像采集与边缘检测")
        capture_picture()

    except Exception as e:
        print(f"主程序异常：{e}")

    finally:
        # 程序退出前释放资源
        if camera_is_init:
            print("摄像头资源释放")
            camera_deinit()

# 如果是主模块运行，则调用 main()
if __name__ == "__main__":
    main()
