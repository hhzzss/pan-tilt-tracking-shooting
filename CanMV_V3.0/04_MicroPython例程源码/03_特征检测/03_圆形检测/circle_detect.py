'''
本程序遵循GPL V3协议, 请遵循协议
实验平台: DshanPI CanMV
开发板文档站点	: https://eai.100ask.net/
百问网学习平台   : https://www.100ask.net
百问网官方B站    : https://space.bilibili.com/275908810
百问网官方淘宝   : https://100ask.taobao.com
'''
import time, os, sys

from media.sensor import *    # 摄像头相关接口
from media.display import *   # 显示屏相关接口
from media.media import *     # 多媒体资源管理接口

# === 配置参数 ===
SENSOR_W, SENSOR_H     = 1280, 960          # 摄像头采集分辨率（原始）
FRAME_W, FRAME_H       = 320, 240           # 实际输出帧大小
LCD_W, LCD_H           = 480, 640           # LCD 屏幕分辨率
CIRCLE_THRESHOLD       = 2000               # 圆检测强度阈值，越高圆越少但更准确
CIRCLE_X_MARGIN        = 10                 # 圆心 X 坐标合并容差
CIRCLE_Y_MARGIN        = 10                 # 圆心 Y 坐标合并容差
CIRCLE_R_MARGIN        = 10                 # 半径合并容差
CIRCLE_R_MIN           = 2                  # 最小检测半径
CIRCLE_R_MAX           = 100                # 最大检测半径
CIRCLE_R_STEP          = 2                  # 半径步进
CIRCLE_COLOR           = (255, 0, 0)        # 检测圆形绘制颜色（红色）

# === 初始化摄像头 ===
sensor = Sensor(width=SENSOR_W, height=SENSOR_H)   # 创建摄像头对象
sensor.reset()                                     # 初始化摄像头
sensor.set_framesize(width=FRAME_W, height=FRAME_H) # 设置图像帧尺寸
sensor.set_pixformat(Sensor.RGB565)                # 设置图像格式为 RGB565

# === 初始化显示屏 ===
Display.init(Display.ST7701, width=LCD_W, height=LCD_H, to_ide=True)          # 初始化 MIPI LCD 和 IDE 显示输出
# Display.init(Display.VIRT, sensor.width(), sensor.height()) # 仅使用 IDE 显示输出（调试用）

# === 初始化媒体系统 ===
MediaManager.init()                                # 启用媒体管理器
sensor.run()                                       # 开始采集图像

# === 主循环：捕获图像并检测圆形 ===
clock = time.clock()

while True:
    clock.tick()                                   # 开始计时（用于FPS计算）
    img = sensor.snapshot()                        # 拍摄一帧图像

    # 在图像中检测圆形
    circles = img.find_circles(
        threshold=CIRCLE_THRESHOLD,
        x_margin=CIRCLE_X_MARGIN,
        y_margin=CIRCLE_Y_MARGIN,
        r_margin=CIRCLE_R_MARGIN,
        r_min=CIRCLE_R_MIN,
        r_max=CIRCLE_R_MAX,
        r_step=CIRCLE_R_STEP
    )

    # 遍历检测到的所有圆
    for c in circles:
        img.draw_circle(c.x(), c.y(), c.r(), color=CIRCLE_COLOR, thickness=2)  # 绘制圆
        print(c)  # 输出圆的参数（圆心坐标、半径、强度）

    # 居中显示图像
    Display.show_image(
        img,
        x=round((LCD_W - sensor.width()) / 2),
        y=round((LCD_H - sensor.height()) / 2)
    )

    print(clock.fps())  # 打印每秒帧率
