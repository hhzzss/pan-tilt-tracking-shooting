'''
本程序遵循GPL V3协议, 请遵循协议
实验平台: DshanPI CanMV
开发板文档站点	: https://eai.100ask.net/
百问网学习平台   : https://www.100ask.net
百问网官方B站    : https://space.bilibili.com/275908810
百问网官方淘宝   : https://100ask.taobao.com
'''
import time, os, gc, sys, math

from media.sensor import *
from media.display import *
from media.media import *

# 图像分辨率为 QVGA 320x240
DETECT_WIDTH = 320
DETECT_HEIGHT = 240

# 追踪黑线 (灰度阈值为0~64)，追踪白线时改为 [(128, 255)]
GRAYSCALE_THRESHOLD = [(0, 64)]

# 设置 ROI 区域，从图像底部到顶部分成3块区域，每块区域有对应权重
ROIS = [
    (0, 200, 320, 40, 0.7),  # 底部 ROI，靠近机器人，权重最大
    (0, 100, 320, 40, 0.3),  # 中间 ROI，次之
    (0,   0, 320, 40, 0.1)   # 顶部 ROI，权重最小
]

# 计算所有 ROI 的总权重
weight_sum = sum(r[4] for r in ROIS)

sensor = None

try:
    # 初始化摄像头
    sensor = Sensor(width=1280, height=960)
    sensor.reset()
    sensor.set_framesize(width=DETECT_WIDTH, height=DETECT_HEIGHT)
    sensor.set_pixformat(Sensor.GRAYSCALE)

    # 初始化显示屏 (使用 3.5 寸 LCD 并启用 IDE 缓冲)
    Display.init(Display.ST7701, width=640, height=480, to_ide=True)

    # 初始化媒体管理器
    MediaManager.init()
    sensor.run()

    clock = time.clock()

    while True:
        clock.tick()

        os.exitpoint()  # 检查是否应退出程序
        img = sensor.snapshot()

        centroid_sum = 0

        for r in ROIS:
            blobs = img.find_blobs(GRAYSCALE_THRESHOLD, roi=r[0:4], merge=True)
            if blobs:
                largest_blob = max(blobs, key=lambda b: b.pixels())

                # 绘制 ROI 边框和十字中心
                img.draw_rectangle(largest_blob.rect())
                img.draw_cross(largest_blob.cx(), largest_blob.cy())

                # 按权重累加中心点 X 坐标
                centroid_sum += largest_blob.cx() * r[4]

        # 计算加权平均的中心位置
        center_pos = centroid_sum / weight_sum

        # 偏移角度计算（图像宽度 320，中心在160，采用三角函数偏移量）
        deflection_angle = -math.atan((center_pos - 160) / 120)
        deflection_angle = math.degrees(deflection_angle)

        # 打印偏移角度
        print("Turn Angle: %f" % deflection_angle)

        # 在图像上绘制偏转角度文字
        img.draw_string_advanced(2, 2, 20, str('%.1f' % deflection_angle), color=(255, 255, 255))

        # 居中方式显示图像（让图像在800x480 LCD 上居中）
        Display.show_image(img, x=round((480 - DETECT_WIDTH) / 2), y=round((360 - DETECT_HEIGHT) / 2))

        print(clock.fps())  # 打印帧率

        gc.collect()

except KeyboardInterrupt:
    print("用户终止程序")
except BaseException as e:
    print(f"异常：{e}")
finally:
    if isinstance(sensor, Sensor):
        sensor.stop()
    Display.deinit()

    os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
    time.sleep_ms(100)

    MediaManager.deinit()
