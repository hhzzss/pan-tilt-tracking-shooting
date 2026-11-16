# C30D 二维云台专用固件

当前跟踪版俯仰软件限位为 **60°～120°**（PWM 约1167～1833μs，中位90°）；点灯容差为 **仅左右误差 ex ±50（不要求上下）**，连续2秒后吸合。舵机跟踪死区仍为±15。首次上板确认支架与线材在扩大后的范围内无干涉。

2026-11-11 跟踪固件 `outputs/firmware/04_tracking_PA3.hex` 已加入 [居中2秒后点灯](outputs/跟踪居中2秒点灯.md)：目标左右误差 ex 在 ±50 内（上下误差不参与）连续满 2000ms 时，PC12 拉低使 LOW 触发继电器吸合；偏离、丢失或串口满 300ms 未更新时释放，并重新计时。启动标识 `TRACKING_RELAY_PC12_V3`，日志增加 `center_ms`、`relay`。

2026-11-11 增加 [PC12 继电器测试](outputs/PC12继电器接线与测试.md)：烧录 `outputs/firmware/07_relay_pc12_test.hex`，PC12 使用开漏、无内部上下拉，先断开 2 秒，再按吸合 1 秒、断开 2 秒循环；此测试不输出舵机 PWM。专用 Keil 工程为 `firmware/C30D_Relay_PC12_Test.uvprojx`。

串口现改用预留IO排针 **PA3 / USART2_RX / AF7**，不再从PD6接收。先烧 [03_uart_monitor_PA3.hex](outputs/firmware/03_uart_monitor_PA3.hex)，启动标识 `UART_RX_PA3_V3`；详见 [PA3接线与测试](outputs/PA3串口接线与测试.md) / [实物丝印标注](outputs/C30D_PA3接线位置.png)。原名03/04固件也已同步改为PA3，旧PD6固件不能接PA3使用。

双轴测试V2：打开 [仅双轴测试的Keil工程](firmware/C30D_DualServo_Test.uvprojx)，或直接烧录 `outputs/firmware/05_dual_sweep.hex`。PC6和PC7同时1400～1600μs往返，完整周期约8秒；日志含 `DUAL_TEST_V2`。

新增 [俯仰舵机单独检查](outputs/俯仰舵机单独检查.md)：Target **06_pitch_sweep** 只让PC7俯仰往返，PC6不输出PWM；**05_dual_sweep** 继续让两轴一起往返。

2026-10-21增加：[Keil双舵机往返测试](outputs/Keil双舵机往返测试.md)。选Target **05_dual_sweep**，两路在中位附近持续缓慢往返，不需要K230，适合当前检查接线。原01～04仍用于分步联调与视觉闭环。

已按轮趣官方绿色四驱 C30D 核对：STM32F407VET6、输入6～17V；PC6/PC7驱动270°/180°位置舵机，K230 TX IO44→预留IO排针PA3接收。当前为包含CMSIS/启动文件/链接脚本的独立工程，非待补引脚的HAL模板。

1. [供电与逐线接线](outputs/供电与逐线连接说明.md)
   （[接线总图](outputs/接线总图.png)）
2. [编译、烧录与分阶段验证/代码解释](outputs/编译烧录与分步验证.md)
3. [官方资料与版本核对](outputs/reference/资料核对.md)
4. [Keil工程](firmware/C30D_PanTilt.uvprojx)；已有 [HEX/BIN](outputs/firmware)
5. [FlyMcu串口烧录双舵机测试](outputs/FlyMcu烧录双舵机测试.md)：使用串口1一键下载Type-C，无需ST-Link。

验证顺序：底座单测→俯仰单测→串口监视（无PWM）→双轴小偏差确认方向→视觉跟随。每阶段单独烧一个HEX。

协议：115200 8N1，ASCII `$T,found,ex,ey\n`，found为0/1，ex/ey为整数-1000～1000，LF或CRLF结束。图像右/下为正，归一化分母为各轴半幅。丢失发 `$T,0,0,0\n`，至少有新有效帧的周期应小于默认300ms超时；推荐20Hz。

功能：两路50Hz PWM、严格串口解析、比例角速度跟随、中心死区、角度和速度限制、丢失/通信超时保持。失联继续输出最后角度PWM；复位则回中，启动回中不受跟随软件限速约束。不要把初次上电当作受控慢速动作。

```powershell
python firmware/build_keil.py
python tests/run_c_checks.py
python tests/run_protocol_checks.py
```

四阶段交叉编译及C/Python主机测试已通过；尚未烧录实板或完成视觉闭环调参。此前人形例程的串口修改副本为 `k230/person_detection_tracking.py`，保留person模型；玩偶检测沿用用户已有模型，用 `pantilt_uart.py`接入。

目录：firmware=可编译源/Keil工程，k230=发送与联调脚本，tests=主机检查，outputs=交付固件/说明/资料/压缩包，work=浏览及构建中间文件。`firmware/Vendor`与人形例程保留上游许可说明。
