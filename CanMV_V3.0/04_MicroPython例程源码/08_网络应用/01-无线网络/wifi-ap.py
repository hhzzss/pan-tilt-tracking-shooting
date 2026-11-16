import network
import time

TARGET_AP = "Programmers"       # 目标接入点名称
CONNECT_KEY = "100asktech"      # 接入验证密码

def wireless_link_setup():
    # 初始化无线客户端模式
    wlan = network.WLAN(network.STA_IF)

    # 激活无线通信硬件
    if not wlan.active():
        wlan.active(True)
    print("无线硬件状态:", wlan.active())  # 输出激活状态

    # 显示初始网络连接状态
    print("初始链路状态:", wlan.status())

    # 扫描周边无线信号
    available_networks = wlan.scan()
    print("扫描到可用网络:")
    for ap_info in available_networks:
        ap_name = ap_info.ssid         # 网络名称
        signal_quality = ap_info.rssi  # 信号质量值
        print(f"网络标识: {ap_name}, 信号强度: {signal_quality}dBm")

    # 尝试建立网络连接
    print(f"正在接入目标网络: {TARGET_AP}...")
    wlan.connect(TARGET_AP, CONNECT_KEY)

    # 连接重试机制（最多5次尝试）
    retry_counter = 5
    while retry_counter > 0:
        if wlan.isconnected():  # 检测连接状态
            break
        retry_counter -= 1
        time.sleep(1)           # 短暂等待后重试
        wlan.connect(TARGET_AP, CONNECT_KEY)
        print(f"剩余尝试次数: {retry_counter}")

    # 等待IP地址分配完成
    while wlan.ifconfig()[0] == '0.0.0.0':
        time.sleep(0.5)

    # 连接结果反馈
    if wlan.isconnected():
        print("\n网络连接建立成功！")
        net_params = wlan.ifconfig()
        print(f"设备IP地址: {net_params[0]}")
        print(f"子网掩码配置: {net_params[1]}")
        print(f"默认网关地址: {net_params[2]}")
        print(f"DNS服务器地址: {net_params[3]}")
    else:
        print("网络连接失败，请检查密码或信号覆盖情况")

# 执行网络连接流程
wireless_link_setup()

# 保持程序运行状态
while True:
    time.sleep(0.5)  # 维持基础运行时序
