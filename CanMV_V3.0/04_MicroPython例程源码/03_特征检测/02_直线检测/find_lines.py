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

# 设置图像采集的分辨率（宽度向上对齐到16的倍数，兼容底层硬件）
DETECT_WIDTH = ALIGN_UP(480, 16)
DETECT_HEIGHT = 640

# 设置角度过滤范围（只检测角度在该范围内的直线）
min_degree = 0
max_degree = 179

# 所有 line 对象都提供以下方法：
# - `theta()`：获取该直线相对于水平线的角度（单位：度）
# - `x1(), y1(), x2(), y2()`：获取直线的两个端点坐标
# - `line()`：返回 [x1, y1, x2, y2] 形式的元组，用于绘图

# 关于负 rho 值的说明：
# 如果一条线的表示是 [theta+0, -rho]，等价于 [theta+180, +rho]

sensor = None  # 全局摄像头对象

# 摄像头初始化函数
def camera_init():
    global sensor

    # 创建 Sensor 对象，设置图像分辨率
    sensor = Sensor(width=DETECT_WIDTH, height=DETECT_HEIGHT)
    sensor.reset()  # 复位传感器

    # 如有需要可以开启水平/垂直镜像
    # sensor.set_hmirror(False)
    # sensor.set_vflip(False)

    sensor.set_framesize(width=DETECT_WIDTH, height=DETECT_HEIGHT)  # 设置输出分辨率
    sensor.set_pixformat(Sensor.RGB565)  # 设置图像格式为 RGB565 彩图
    Display.init(Display.ST7701, width=DETECT_WIDTH, height=DETECT_HEIGHT, fps=60, to_ide=True)  # 初始化虚拟显示（IDE 输出）
    MediaManager.init()  # 初始化媒体资源管理器
    sensor.run()  # 启动摄像头采集

# 摄像头资源释放函数
def camera_deinit():
    global sensor
    sensor.stop()  # 停止采集
    Display.deinit()  # 释放显示设备
    os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)  # IDE 模式休眠标记
    time.sleep_ms(100)  # 延时确保退出稳定
    MediaManager.deinit()  # 释放媒体资源（缓存池）

# 图像采集与线段检测主循环
def capture_picture():
    fps = time.clock()  # 用于帧率统计

    while True:
        fps.tick()  # 本帧开始计时

        try:
            os.exitpoint()  # IDE 中断控制支持
            global sensor
            img = sensor.snapshot()  # 采集一帧图像（RGB565 彩图）

            # 开始进行直线检测，返回 line 对象列表
            # 参数说明：
            # - threshold：阈值，决定哪些直线被认为是“有效直线”
            #   较小的阈值将检测更多细小线条，较大的值可排除弱边缘线
            # - theta_margin/rho_margin：控制相似直线合并容差，单位分别为角度/像素

            for l in img.find_lines(threshold=1000, theta_margin=25, rho_margin=25):
                if (min_degree <= l.theta()) and (l.theta() <= max_degree):  # 角度过滤
                    img.draw_line([v for v in l.line()], color=(255, 0, 0))  # 绘制红色直线
                    print(l)  # 打印直线参数信息（theta、rho、坐标等）

            Display.show_image(img)  # 将结果图像显示在 IDE 中
            img = None  # 释放图像引用

            gc.collect()  # 执行垃圾回收，避免内存堆积
            print(fps.fps())  # 输出当前帧率
        except KeyboardInterrupt as e:
            print("用户中断运行：", e)
            break
        except BaseException as e:
            print(f"运行异常：{e}")
            break

# 主函数
def main():
    os.exitpoint(os.EXITPOINT_ENABLE)  # 启用 IDE 中断控制
    camera_is_init = False  # 标志变量，避免未初始化直接释放资源

    try:
        print("摄像头初始化中...")
        camera_init()
        camera_is_init = True
        print("开始图像采集与线段检测...")
        capture_picture()
    except Exception as e:
        print(f"主程序异常：{e}")
    finally:
        if camera_is_init:
            print("释放摄像头资源...")
            camera_deinit()

# 程序入口点
if __name__ == "__main__":
    main()
