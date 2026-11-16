'''
本程序遵循GPL V3协议, 请遵循协议
实验平台: DshanPI CanMV
开发板文档站点	: https://eai.100ask.net/
百问网学习平台   : https://www.100ask.net
百问网官方B站    : https://space.bilibili.com/275908810
百问网官方淘宝   : https://100ask.taobao.com
'''
import time
import os
import sys

from media.sensor import Sensor, CAM_CHN_ID_0
from media.display import Display
from media.media import MediaManager

# -------------------------------
# 参数配置区
# -------------------------------

# 显示模式选择：'VIRT' 虚拟显示器，'LCD' MIPI 显示屏，'HDMI' HDMI 转接板
DISPLAY_MODE = "LCD"

# 根据显示模式设置显示器宽高
DISPLAY_CONFIG = {
    "VIRT": {"width": 1920, "height": 1080, "driver": Display.VIRT},
    "LCD":  {"width": 640,  "height": 480,  "driver": Display.ST7701},
}

# 获取当前显示配置
if DISPLAY_MODE not in DISPLAY_CONFIG:
    raise ValueError("不支持的 DISPLAY_MODE，请使用 'VIRT'、'LCD'")

config = DISPLAY_CONFIG[DISPLAY_MODE]
DISPLAY_WIDTH = config["width"]
DISPLAY_HEIGHT = config["height"]
DISPLAY_DRIVER = config["driver"]

# -------------------------------
# 主程序
# -------------------------------

sensor = None

try:
    print("[INFO] 启动摄像头测试程序")

    # 初始化摄像头
    sensor = Sensor()
    sensor.reset()

    # 设置图像输出格式与分辨率
    sensor.set_framesize(width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, chn=CAM_CHN_ID_0)
    sensor.set_pixformat(Sensor.RGB888, chn=CAM_CHN_ID_0)

    # 初始化显示器
    Display.init(
        DISPLAY_DRIVER,
        width=DISPLAY_WIDTH,
        height=DISPLAY_HEIGHT,
        fps=60,
        to_ide=True  # 即使是物理屏幕，仍可在IDE中同步预览
    )

    # 启动媒体缓冲管理器
    MediaManager.init()

    # 启动摄像头采集
    sensor.run()
    print("[INFO] 摄像头已启动，分辨率: {}x{}".format(DISPLAY_WIDTH, DISPLAY_HEIGHT))

    # 主循环：采集图像并绘制图形
    while True:
        os.exitpoint()  # 监听 IDE 停止命令

        # 捕获一帧图像
        img = sensor.snapshot(chn=CAM_CHN_ID_0)

        # 图像绘制内容
        img.draw_rectangle(30, 30, 100, 50, color=(0, 255, 0), thickness=5)                 # 绿色矩形
        img.draw_circle(200, 250, 50, color=(255, 0, 0), thickness=3)                      # 红色圆形
        img.draw_line(300, 250, 400, 200, color=(0, 0, 255), thickness=2)                  # 蓝色线
        img.draw_string_advanced(50, 100, 32, "你好, DshanPI-CanMV V3!",
                                 color=(255, 255, 0), scale=2)                              # 黄色字符串
        img.draw_cross(350, 300, color=(255, 255, 255), size=20, thickness=2)              # 白色十字

        # 显示图像
        Display.show_image(img)

except KeyboardInterrupt:
    print("[INFO] 用户中断退出")
except Exception as e:
    print("[ERROR] 运行异常：", e)
finally:
    print("[INFO] 正在清理资源...")
    if isinstance(sensor, Sensor):
        sensor.stop()
    Display.deinit()
    os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
    time.sleep_ms(100)
    MediaManager.deinit()
    print("[INFO] 清理完成，程序退出")
