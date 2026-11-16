'''
本程序遵循GPL V3协议, 请遵循协议
实验平台: DshanPI CanMV
开发板文档站点	: https://eai.100ask.net/
百问网学习平台   : https://www.100ask.net
百问网官方B站    : https://space.bilibili.com/275908810
百问网官方淘宝   : https://100ask.taobao.com
'''
from machine import ADC
import time

# 创建 ADC0 通道的对象（连接到排针32）
adc = ADC(0)  # 表示 ADC 通道0

while True:
    # 读取原始采样值（16位，范围0~65535）
    print(adc.read_u16())

    # 读取转换后的电压值（单位为 V），保留两位小数
    # 注意：ADC0/ADC1 实际采样范围为 0~1.8V，但引脚电压范围是 0~3.6V，因此需要乘以2
    print('%.2f' % (adc.read_uv() / 1000000 * 2), "V")

    time.sleep(1)  # 每秒采样一次
