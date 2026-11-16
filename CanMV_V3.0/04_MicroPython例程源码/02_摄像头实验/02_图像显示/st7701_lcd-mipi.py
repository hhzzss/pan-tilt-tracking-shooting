'''
  Copyright (C) 2008-2023 深圳百问网科技有限公司
  All rights reserved

 免责声明: 百问网编写的程序, 用于商业用途请遵循GPL许可, 百问网不承担任何后果！

 本程序遵循GPL V3协议, 请遵循协议
 百问网学习平台   : https://www.100ask.net
 百问网交流社区   : https://forums.100ask.net
 百问网官方B站    : https://space.bilibili.com/275908810
 本程序所用开发板 : DshanPI-CanMV开发板
 开发板文档站点	 ： https://eai.100ask.net/
 百问网官方淘宝   : https://100ask.taobao.com
 联系我们(E-mail) : weidongshan@100ask.net
'''
import time, os, urandom, sys

from media.display import *
from media.media import *

DISPLAY_WIDTH = 640    # 显示屏宽度（像素）
DISPLAY_HEIGHT = 480   # 显示屏高度（像素）

def display_test():
    """显示测试主函数：在屏幕上随机位置绘制彩色文本"""
    print("显示测试开始")

    # 创建一张用于绘图的图像，格式为 ARGB8888
    img = image.Image(DISPLAY_WIDTH, DISPLAY_HEIGHT, image.ARGB8888)

    # 初始化 LCD 显示屏作为输出设备，并允许同时将图像输出到 IDE
    Display.init(Display.ST7701, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, to_ide=True)
    # 初始化多媒体管理器
    MediaManager.init()

    try:
        while True:
            # 清空图像（填充黑色）
            img.clear()
            # 随机绘制 10 行文字
            for i in range(10):
                x = (urandom.getrandbits(11) % img.width())      # 随机 X 坐标
                y = (urandom.getrandbits(11) % img.height())     # 随机 Y 坐标
                r = (urandom.getrandbits(8))                     # 红色分量 (0-255)
                g = (urandom.getrandbits(8))                     # 绿色分量
                b = (urandom.getrandbits(8))                     # 蓝色分量
                size = (urandom.getrandbits(30) % 64) + 32       # 字体大小 (32~95)

                # 在随机位置绘制指定文本，支持中英文混合，颜色随机
                img.draw_string_advanced(x, y, size, "Hello World!，你好世界！！！", color=(r, g, b))

            # 将绘制好的图像显示到屏幕上
            Display.show_image(img)

            time.sleep(1)          # 每秒更新一次画面
            os.exitpoint()         # 检查退出标志（支持 Ctrl+C 或程序退出）
    except KeyboardInterrupt as e:
        print("用户中断: ", e)
    except BaseException as e:
        import sys
        sys.print_exception(e)

    # 释放显示资源
    Display.deinit()
    os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
    time.sleep_ms(100)
    # 释放多媒体缓冲区
    MediaManager.deinit()

if __name__ == "__main__":
    os.exitpoint(os.EXITPOINT_ENABLE)   # 使能退出点检查
    display_test()
