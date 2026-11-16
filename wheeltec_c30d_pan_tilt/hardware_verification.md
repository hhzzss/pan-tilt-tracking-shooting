# 硬件核对结果

已取得官方商品型号/参数/接口图，并用带WHEELTEC页脚的第三方原理图交叉核对。当前工程是可编译的 F407 CMSIS 工程，原 HAL 模板已替换。

| 项目 | 核对结果 | 工程使用 |
|---|---|---|
| C30D普通绿色四驱 | STM32F407VET6，6～17V输入 | 512KB Flash，128KB普通SRAM；不使用额外64KB CCM |
| 两路舵机 | PC6、PC7 | TIM3 CH1/CH2，AF2，50Hz，500～2500μs |
| 预留IO PA3（当前接收） | 用户背面照片标有PA3；镜像原理图引出PA3 | USART2_RX，AF7；只启用接收，不驱动PA2 |
| 蓝牙接口（旧接法） | 5V / G / D6 / D5 | PD6 USART2_RX，PD5 USART2_TX，AF7；当前固件不使用 |
| 板载串口1 | PA9/PA10经CH9102到Type-C | 仅PA9发日志115200；刷写走SWD主路径 |
| 板载串口3 | PD8/PD9经另一CH9102到Type-C | 本项目不用 |
| SWD | PA13 SWDIO、PA14 SWCLK | ST-Link下载 |
| DshanPI CanMV V3 | J6-2=TX IO44，J6-4=GND | K230 UART2发送 |
| 舵机供电 | S20F180/270为5～6.5V，1.8A@5V/只 | 外部稳压5V/5A支路，两只共用 |

详细原图、来源和板次限制见 outputs/reference/资料核对.md；接线步骤见 outputs/供电与逐线连接说明.md。实际插线依照丝印与J6编号，不依靠照片方向猜排针次序。
