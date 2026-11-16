import os
import sys
import time

from media.sensor import *
from media.display import *
from media.media import *

CAMERA_ID = 0       # CSI0 用 0，CSI2 用 2
sensor = None
display_ready = False
media_ready = False

try:
    print("开始初始化摄像头")

    sensor = Sensor(id=CAMERA_ID)
    sensor.reset()
    sensor.set_framesize(width=640, height=480)
    sensor.set_pixformat(Sensor.YUV420SP)

    bind_info = sensor.bind_info()
    Display.bind_layer(**bind_info, layer=Display.LAYER_VIDEO1)
    Display.init(Display.VIRT, width=640, height=480, to_ide=True)
    display_ready = True

    MediaManager.init()
    media_ready = True

    sensor.run()
    print("摄像头初始化成功")

    while True:
        os.exitpoint()

except KeyboardInterrupt:
    print("程序被停止")

except BaseException as e:
    sys.print_exception(e)

finally:
    if sensor is not None:
        sensor.stop()

    if display_ready:
        Display.deinit()

    if media_ready:
        MediaManager.deinit()
