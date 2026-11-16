# 改用预留IO的PA3接收K230

适用当前普通绿色四驱C30D / STM32F407VET6与DshanPI CanMV V3。PA3支持USART2_RX，复用号AF7；硬件UART不能随意选任意GPIO。当前工程03串口监视与04跟随均已切换为PA3；必须重新烧录。

## 两根线

先断开两板电源，再拔掉原先接PD6的信号线。

| K230 | C30D |
|---|---|
| J6-2：TX / IO44 | 预留IO排针 **PA3** |
| J6-4：GND | 预留IO排针 **GND** |

按用户照片方向，PA3在预留IO丝印表左列，PA6下方、PA2上方，与右列PC3同行。GND可用右列与5V同行、PA7/PD15上一行的地针。见 [背面丝印标注](C30D_PA3接线位置.png)。图中圈出名称，连接名称对应的排针；不要插到相邻PA2/PC3或用附近任意焊点代替。J6的固定焊脚不算四个信号针。

两板之间只接上表两根线。K230 J6-1的3.3V、J6-3的RX，C30D的5V/3V3/PA2都留空。电源仍按原接线分别供电并共地；PC6/PC7舵机线保持原接法。不要同时把另一TX接到PA3。

## 重新烧录并检查计数

1. 关闭舵机电源，支撑俯仰机构。关闭串口助手，FlyMcu选择C30D串口1对应COM、115200，以及原已使用的 `DTR的低电平复位,RTS高电平进BootLoader`。
2. 加载 [03_uart_monitor_PA3.hex](firmware/03_uart_monitor_PA3.hex)，下载并校验，运行程序。此文件与本次重新编译的 `03_uart_monitor.hex` 内容相同，带PA3的文件名用于区分旧版PD6固件。
3. 关闭FlyMcu，再打开串口助手，115200 / 8N1 / 无流控。需要时复位，应看到：

```text
UART_RX_PA3_V3: USART2 RX=PA3 AF7; rx=received bytes; PWM OFF
```

4. 在CanMV IDE运行现有发送脚本 `../..\CanMV_V3.0\04_MicroPython例程源码\test_connect.py`，或项目的独立串口测试。**K230程序不用改，也不用写入main.py。**仍从UART2/IO44按115200、8N1发送 `$T,0,0,0\n`（末尾为真正换行）。
5. C30D应出现rx与ok持续增长：默认每秒20条9字节数据，约每秒rx增加180、ok增加20。bad、uart_err应保持不增长。stage=3时active=0正常，两路PWM关闭；pwm=1500/1500是内部初值，不表示实际输出。

若仍rx=0，不能仅凭K230发送计数判断连通；继续按 [零接收排查](串口零接收排查.md) 做K230本地回环或独立3.3V USB-TTL测试。

## Keil与后续跟随

源工程 [C30D_PanTilt.uvprojx](../firmware/C30D_PanTilt.uvprojx)，选择Target **03_uart_monitor**，F7编译。Keil生成的HEX在 `work/uvision/03_uart_monitor/`，同样是PA3版；名字带PA3的交付副本在outputs/firmware，由命令构建脚本生成。

确认通信后使用 [04_tracking_PA3.hex](firmware/04_tracking_PA3.hex) 再验证方向和视觉跟随，接线不变。不要重新烧录此前保存的PD6旧版04。

本次源码变更：BSP将USART2接收从GPIOD6改为GPIOA3/AF7并启用上拉；只启用接收，不驱动PA2/PD5；main增加PA3版本启动提示。USART1电脑日志、协议、PWM与控制逻辑保持原行为。

已编译与主机检查；尚未在两块实物上验证PA3通信。换脚有助于消除接口定位困难，不能据此断言原故障原因已经确定。
