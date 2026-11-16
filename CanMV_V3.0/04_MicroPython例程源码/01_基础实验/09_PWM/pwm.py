'''
本程序遵循GPL V3协议, 请遵循协议
实验平台: DshanPI CanMV
开发板文档站点	: https://eai.100ask.net/
百问网学习平台   : https://www.100ask.net
百问网官方B站    : https://space.bilibili.com/275908810
百问网官方淘宝   : https://100ask.taobao.com
'''
from machine import Pin, PWM
from machine import FPIOA
import time

# 配置引脚42为PWM0功能
fpioa = FPIOA()
fpioa.set_function(42, FPIOA.PWM0)

# 初始化舵机PWM对象（PWM通道0，频率50Hz）
S1 = PWM(0, 50, duty=0, enable=True)

def Servo(servo, angle):
    '''
    舵机角度控制函数
    角度范围：-90 到 90
    对应 PWM 占空比范围：2.5% ~ 12.5%
    '''
    duty = (angle + 90) / 180 * 10 + 2.5  # 将角度映射到 duty 占空比
    servo.duty(duty)

# 定义旋转角度顺序：先前进到 90，再逐步退回到 -90
angles_forward = [-90, -45, 0, 45, 90]
angles_backward = [45, 0, -45, -90]

while True:
    # 顺时针旋转
    for angle in angles_forward:
        Servo(S1, angle)
        time.sleep(0.5)

    # 逆时针回到初始位置
    for angle in angles_backward:
        Servo(S1, angle)
        time.sleep(0.5)
