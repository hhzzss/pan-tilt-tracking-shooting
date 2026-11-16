'''
本程序遵循GPL V3协议, 请遵循协议
实验平台: DshanPI CanMV
开发板文档站点	: https://eai.100ask.net/
百问网学习平台   : https://www.100ask.net
百问网官方B站    : https://space.bilibili.com/275908810
百问网官方淘宝   : https://100ask.taobao.com
'''
from libs.PipeLine import ScopedTiming             # 只使用计时器，不使用默认摄像头及实体屏配置
from libs.AIBase import AIBase                    # AI推理基础类（封装模型加载、推理等基础操作）
from libs.AI2D import Ai2d                        # 图像预处理类（图像pad、resize等）
import os
from media.sensor import Sensor, CAM_CHN_ID_0, CAM_CHN_ID_2
from media.display import Display
from media.media import *                         # 媒体库（摄像头获取图像、显示图像等）
from time import *                                # 时间模块（包含sleep、time等）
import nncase_runtime as nn                       # NNCase推理引擎库，进行模型加载与执行
import ulab.numpy as np                           # ulab库：兼容numpy的轻量数组库，适合MCU等资源受限平台
import time
import utime                                      # 更轻量的时间库（适用于MCU）
import image                                      # 图像处理相关API（例如绘制、图像信息提取等）
import random                                     # 随机数库（未在此代码中使用）
import gc                                          # 垃圾回收模块，用于手动释放内存
import sys
import aicube                                     # 自定义aicube库，包含anchor-based目标检测后处理
from machine import UART, FPIOA


def select_target(dets, image_size, target_class=0):
    # 多目标时选择面积最大的目标；坐标使用 AI 采集图像，不使用模型输入坐标。
    best = None
    best_area = 0
    if dets is None:
        return None
    width, height = image_size
    for box in dets:
        if int(box[0]) != target_class:
            continue
        x1 = max(0, min(width, float(box[2])))
        y1 = max(0, min(height, float(box[3])))
        x2 = max(0, min(width, float(box[4])))
        y2 = max(0, min(height, float(box[5])))
        if x2 <= x1 or y2 <= y1:
            continue
        area = (x2 - x1) * (y2 - y1)
        if area > best_area:
            best_area = area
            best = (x1, y1, x2, y2)
    return best


def target_error(target, image_size):
    if target is None:
        return (0, 0, 0)
    width, height = image_size
    cx = (target[0] + target[2]) / 2
    cy = (target[1] + target[3]) / 2
    # 各轴按半幅归一化：右/下为正，范围 -1000~1000；并非舵机角度。
    dx = max(-1000, min(1000, int(round((cx - width / 2) * 2000 / width))))
    dy = max(-1000, min(1000, int(round((cy - height / 2) * 2000 / height))))
    return (1, dx, dy)


def send_tracking(uart, tracking):
    packet = ("$T,%d,%d,%d\n" % tracking).encode("ascii")
    if uart.write(packet) != len(packet):
        # 不继续发送截断帧；交由主循环退出和 C30D 接收超时保护处理。
        raise OSError("UART tracking frame write incomplete")

# 检测应用类：兼容本次 sabo AnchorBaseDet 模型，并保留原类名供现有入口调用。
class PersonDetectionApp(AIBase):
    def __init__(self, kmodel_path, model_input_size, labels, anchors,
                 confidence_threshold=0.2, nms_threshold=0.5, nms_option=False,
                 strides=[8, 16, 32], rgb888p_size=[224, 224], display_size=[1920, 1080], debug_mode=0):
        super().__init__(kmodel_path, model_input_size, rgb888p_size, debug_mode)
        # 参数保存
        self.kmodel_path = kmodel_path
        self.model_input_size = model_input_size         # 当前训练模型为 320x320
        self.labels = labels                             # 当前模型类别为 ["sabo"]
        self.anchors = anchors                           # 锚框参数
        self.strides = strides                           # 每层输出特征图的步长
        self.confidence_threshold = confidence_threshold # 用于过滤低置信度框
        self.nms_threshold = nms_threshold               # 非极大值抑制的IOU阈值
        self.nms_option = nms_option                     # 是否使用NMS优化加速
        self.rgb888p_size = [ALIGN_UP(rgb888p_size[0], 16), rgb888p_size[1]]  # 图像采集分辨率，宽度对齐到16
        self.display_size = [ALIGN_UP(display_size[0], 16), display_size[1]] # 显示图像分辨率
        self.debug_mode = debug_mode

        # 创建图像预处理对象
        self.ai2d = Ai2d(debug_mode)
        self.ai2d.set_ai2d_dtype(nn.ai2d_format.NCHW_FMT, nn.ai2d_format.NCHW_FMT, np.uint8, np.uint8)

    # 配置图像预处理流程，包括padding与resize策略
    def config_preprocess(self, input_image_size=None):
        with ScopedTiming("set preprocess config", self.debug_mode > 0):
            ai2d_input_size = input_image_size if input_image_size else self.rgb888p_size
            # 获取上下左右padding数值
            top, bottom, left, right = self.get_padding_param()
            # 与配套 AnchorBaseDet 部署例程一致，letterbox 使用 114 灰色填充。
            self.ai2d.pad([0, 0, 0, 0, top, bottom, left, right], 0, [114, 114, 114])
            self.ai2d.resize(nn.interp_method.tf_bilinear, nn.interp_mode.half_pixel)  # 缩放方法
            self.ai2d.build([1, 3, ai2d_input_size[1], ai2d_input_size[0]],
                            [1, 3, self.model_input_size[1], self.model_input_size[0]])

    # 推理结果后处理（坐标反算、NMS、过滤）
    def postprocess(self, results):
        with ScopedTiming("postprocess", self.debug_mode > 0):
            dets = aicube.anchorbasedet_post_process(
                results[0], results[1], results[2],
                self.model_input_size, self.rgb888p_size,
                self.strides, len(self.labels),
                self.confidence_threshold, self.nms_threshold,
                self.anchors, self.nms_option
            )
            return dets

    # 绘制检测结果到屏幕
    def draw_result(self, osd_img, dets, target=None, tracking=(0, 0, 0)):
        with ScopedTiming("display_draw", self.debug_mode > 0):
            if dets:
                osd_img.clear()
                for det_box in dets:
                    # 反归一化为实际坐标
                    x1, y1, x2, y2 = det_box[2], det_box[3], det_box[4], det_box[5]
                    w = float(x2 - x1) * self.display_size[0] // self.rgb888p_size[0]
                    h = float(y2 - y1) * self.display_size[1] // self.rgb888p_size[1]
                    x1 = int(x1 * self.display_size[0] // self.rgb888p_size[0])
                    y1 = int(y1 * self.display_size[1] // self.rgb888p_size[1])
                    x2 = int(x2 * self.display_size[0] // self.rgb888p_size[0])
                    y2 = int(y2 * self.display_size[1] // self.rgb888p_size[1])

                    # 保留靠边目标，否则正需要云台转动时却看不到目标框。
                    if w <= 0 or h <= 0:
                        continue

                    # 绘制检测框及文字
                    osd_img.draw_rectangle(x1, y1, int(w), int(h), color=(255, 0, 255, 0), thickness=2)
                    osd_img.draw_string_advanced(x1, max(0, y1 - 50), 32, " " + self.labels[det_box[0]] + " " + str(round(det_box[1], 2)), color=(255, 0, 255, 0))
            else:
                osd_img.clear()

            center_x, center_y = self.display_size[0] // 2, self.display_size[1] // 2
            color = (255, 255, 255, 0)
            osd_img.draw_line(center_x - 10, center_y, center_x + 10, center_y, color=color, thickness=2)
            osd_img.draw_line(center_x, center_y - 10, center_x, center_y + 10, color=color, thickness=2)
            if target is not None:
                sx = self.display_size[0] / self.rgb888p_size[0]
                sy = self.display_size[1] / self.rgb888p_size[1]
                tx = int((target[0] + target[2]) / 2 * sx)
                ty = int((target[1] + target[3]) / 2 * sy)
                osd_img.draw_rectangle(int(target[0] * sx), int(target[1] * sy),
                                       max(1, int((target[2] - target[0]) * sx)),
                                       max(1, int((target[3] - target[1]) * sy)), color=color, thickness=3)
                osd_img.draw_line(center_x, center_y, tx, ty, color=color, thickness=2)
                osd_img.draw_cross(tx, ty, color=color, size=8, thickness=2)
                text = "dx=%d dy=%d" % (tracking[1], tracking[2])
            else:
                text = "NO TARGET"
            osd_img.draw_string_advanced(0, 0, 24, text, color=color)

    # 计算padding值，使图像按模型输入比例居中
    def get_padding_param(self):
        dst_w, dst_h = self.model_input_size
        input_width, input_high = self.rgb888p_size
        ratio_w = dst_w / input_width
        ratio_h = dst_h / input_high
        ratio = min(ratio_w, ratio_h)
        new_w = int(ratio * input_width)
        new_h = int(ratio * input_high)
        dw = (dst_w - new_w) / 2
        dh = (dst_h - new_h) / 2
        top = int(round(dh - 0.1))
        bottom = int(round(dh + 0.1))
        left = int(round(dw - 0.1))
        right = int(round(dw + 0.1))
        return top, bottom, left, right

# 主程序入口：初始化系统并持续检测
if __name__ == "__main__":
    camera_id = 0  # 摄像头连接 CSI0，与输出通道编号无关
    rgb888p_size = [640, 480]  # 采集分辨率与模型输入 320x320 相互独立
    display_size = [640, 480]

    # 与资料自带 uart.py 一致：这里是 IO 编号，不是排针的第 44/45 脚。
    uart_tx_pin = 44  # K230 TX -> C30D 所选 UART 的 RX，双方 GND 共地
    uart_rx_pin = 45  # 当前不接收数据，可不接线
    uart_baudrate = 115200
    send_interval_ms = 50  # 最多 20Hz；实际发送速度受推理帧率限制
    target_class = 0       # deploy_config.json 中唯一类别 sabo 的索引

    # 来自 E:\实验\model\mp_deployment_source\deploy_config.json（AnchorBaseDet）。
    # 将 model 文件夹中的 mp_deployment_source 整个复制到 SD 卡的 /model/ 下。
    kmodel_path = "/sdcard/model/mp_deployment_source/best_AnchorBaseDet_can2_5_s_20261020171350.kmodel"
    model_input_size = [320, 320]
    confidence_threshold = 0.4
    nms_threshold = 0.5
    labels = ["sabo"]
    anchors = [61, 132, 76, 153, 102, 142,
               96, 182, 105, 201, 120, 190,
               113, 238, 132, 255, 166, 260]
    nms_option = False

    sensor = None
    person_det = None
    uart = None
    display_ready = False
    media_ready = False
    stage = "startup"
    try:
        os.exitpoint(os.EXITPOINT_ENABLE)
        stage = "tracking UART2"
        print("[Init]", stage)
        fpioa = FPIOA()
        fpioa.set_function(uart_tx_pin, fpioa.UART2_TXD)
        fpioa.set_function(uart_rx_pin, fpioa.UART2_RXD)
        uart = UART(UART.UART2, baudrate=uart_baudrate, bits=UART.EIGHTBITS,
                    parity=UART.PARITY_NONE, stop=UART.STOPBITS_ONE)
        send_tracking(uart, (0, 0, 0))
        print("[OK] UART2 TX=IO%d RX=IO%d baud=%d" % (uart_tx_pin, uart_rx_pin, uart_baudrate))
        stage = "camera CSI0"
        print("[Init]", stage)
        sensor = Sensor(id=camera_id)
        sensor.reset()
        sensor.set_framesize(width=display_size[0], height=display_size[1], chn=CAM_CHN_ID_0)
        sensor.set_pixformat(Sensor.YUV420SP, chn=CAM_CHN_ID_0)

        # 同一 CSI0 摄像头的通道 2 提供 AI 输入，不能删去。
        sensor.set_framesize(width=rgb888p_size[0], height=rgb888p_size[1], chn=CAM_CHN_ID_2)
        sensor.set_pixformat(Sensor.RGBP888, chn=CAM_CHN_ID_2)

        stage = "IDE display"
        print("[Init]", stage)
        osd_img = image.Image(display_size[0], display_size[1], image.ARGB8888)
        bind_info = sensor.bind_info(chn=CAM_CHN_ID_0)
        Display.bind_layer(**bind_info, layer=Display.LAYER_VIDEO1)
        Display.init(Display.VIRT, width=display_size[0], height=display_size[1], to_ide=True)
        display_ready = True

        stage = "media buffers"
        print("[Init]", stage)
        MediaManager.init()
        media_ready = True
        stage = "camera run"
        sensor.run()
        print("[OK] camera CSI0 + IDE preview")

        stage = "model load"
        print("[Init]", stage, kmodel_path)
        person_det = PersonDetectionApp(
            kmodel_path,
            model_input_size=model_input_size,
            labels=labels,
            anchors=anchors,
            confidence_threshold=confidence_threshold,
            nms_threshold=nms_threshold,
            nms_option=nms_option,
            strides=[8, 16, 32],
            rgb888p_size=rgb888p_size,
            display_size=display_size,
            debug_mode=0
        )
        stage = "AI2D preprocess"
        print("[Init]", stage)
        person_det.config_preprocess()
        first_frame = True
        last_send_ms = time.ticks_ms()
        last_found = 0
        while True:
            os.exitpoint()  # 检查是否退出循环
            with ScopedTiming("total", 0):
                stage = "camera frame"
                frame = sensor.snapshot(chn=CAM_CHN_ID_2)
                img = frame.to_numpy_ref()
                stage = "inference/postprocess"
                res = person_det.run(img)
                if first_frame:
                    print("[OK] first inference, detections:", len(res) if res is not None else 0)
                    first_frame = False
                stage = "target/UART"
                target = select_target(res, rgb888p_size, target_class)
                tracking = target_error(target, rgb888p_size)
                now = time.ticks_ms()
                # 发现/丢失时立即通知；每帧先计算最新误差，避免重发旧坐标。
                if tracking[0] != last_found or time.ticks_diff(now, last_send_ms) >= send_interval_ms:
                    send_tracking(uart, tracking)
                    last_send_ms = now
                    last_found = tracking[0]
                stage = "draw/display"
                person_det.draw_result(osd_img, res, target, tracking)
                Display.show_image(osd_img, 0, 0, Display.LAYER_OSD3)
                gc.collect()
    except KeyboardInterrupt:
        print("[Stop] user stopped")
    except BaseException as e:
        print("[FAIL] stage:", stage)
        sys.print_exception(e)
    finally:
        # 正常停止/异常退出尽力清除旧目标；断电/死机仍需 C30D 自己检测超时。
        if uart is not None:
            try:
                send_tracking(uart, (0, 0, 0))
            except BaseException as e:
                print("[Cleanup] UART stop frame")
                sys.print_exception(e)
        # 某项清理失败时仍继续释放其余已初始化的资源。
        cleanup = []
        if uart is not None:
            cleanup.append(("uart", uart.deinit))
        if person_det is not None:
            cleanup.append(("model", person_det.deinit))
        if sensor is not None:
            cleanup.append(("camera", sensor.stop))
        if display_ready:
            cleanup.append(("display", Display.deinit))
        for name, release in cleanup:
            try:
                release()
            except BaseException as e:
                print("[Cleanup]", name)
                sys.print_exception(e)
        os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
        time.sleep_ms(100)
        if media_ready:
            MediaManager.deinit()
