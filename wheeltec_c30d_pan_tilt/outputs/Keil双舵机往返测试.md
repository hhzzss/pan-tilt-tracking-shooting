# 用Keil烧录双舵机往返测试

需要单独检查俯仰时，选择新Target **06_pitch_sweep**，操作见 [俯仰舵机单独检查](俯仰舵机单独检查.md)。本页的 **05_dual_sweep** 同时检查底座和俯仰。

已有FlyMcu和USB数据线时，可在Keil编译后按 [FlyMcu烧录说明](FlyMcu烧录双舵机测试.md) 下载同一份HEX，不需要ST-Link。

现在测试接线用 `05_dual_sweep`，不需要K230参与。C30D为普通绿色四驱STM32F407VET6；底座信号接PC6，俯仰信号接PC7，均为TIM3输出，50Hz。

## 程序动作

上电/复位后两路先输出1500μs保持2秒，再同时按以下脉宽循环：

`1500 → 1600 → 1400 → 1600 → 1400 → …`

每20ms变化1μs，端点间单程约4秒，一个完整往返约8秒。两轴同时动：底座约121.5°～148.5°，俯仰约81°～99°（舵机内部角度，安装后的方向以实物为准）。初始幅度小；这份程序用来观察接线，不是视觉搜寻策略。停止动作需要关闭舵机电源；按复位只会重新回中并开始往返。

首次运行松开负载/确认机构在中位附近可自由移动。启动回中是直接中位指令，不受后续扫动限速约束。若顶住、持续异响或电源掉压，立即关舵机电源检查。

专用工程 `firmware/C30D_DualServo_Test.uvprojx` 只有双轴测试目标，适合直接打开编译；串口日志版本标识为 `DUAL_TEST_V2`。

## 1. 打开工程并选择测试Target

1. 双击工程 `..\firmware\C30D_PanTilt.uvprojx`。
2. 在Keil顶部Target下拉框选 **05_dual_sweep**。选它才会跑往返测试；01/02只是单轴回中，04需要串口目标才会跟随。
3. 按 **F7** 编译。使用Arm Compiler6；若本机路径不同，在工程的Arm Compiler设置中选择已安装版本。本次已经用本机Keil的Compiler6.7验证，0错误、0警告。

新动作代码在 `firmware/Stages/servo_sweep_test.c`，它负责2秒回中等待、缓慢改变两路PWM、端点换向；`main.c`在PT_STAGE=5时调用它。范围等参数集中在 `pantilt_config.h` 的PT_SWEEP项。

## 2. Keil直接下载仍需下载通道

Keil是开发软件，ST-Link是USB到SWD的下载器。**可以完全在Keil里编译、下载，不必另开CubeProgrammer，但需要ST-Link或同类受支持下载器。**只有电脑USB线接C30D板载CH9102串口时，不能选择ST-Link然后直接按F8；那条线路需要厂家串口下载工具，或额外配置外部下载命令。本工程没有自动调用串口烧录软件。

ST-Link连接（C30D独立供电，电机使能关闭）：

| 下载器 | C30D |
|---|---|
| SWDIO | DIO / PA13 |
| SWCLK | CLK / PA14 |
| GND | GND |
| 正规下载器VTref（电压检测输入） | 板上3.3V参考 |
| NRST（可选） | 板复位NRST |

廉价ST-Link的“3.3V”针可能是电源输出，不是VTref，不要与已供电板的3.3V输出并接；按下载器实际定义处理。它也不能给两只舵机供电。C30D主电源开关打开，舵机烧录期间可先关闭电源。

## 3. Keil下载设置（首次配置）

1. 点击 **Options for Target**（魔术棒，或Alt+F7）。
2. **Device** 页面选择STMicroelectronics的 **STM32F407VE/STM32F407VETx** 对应512KB Flash型号。若列表没有F407，安装Keil官方 **STM32F4xx_DFP** 器件包；随工程提供的CMSIS足够编译，但Keil烧录还需要正确Flash算法。不要选F103或F407VG（1MB）代替。
3. **Debug** 页面选择 **Use: ST-Link Debugger** → **Settings**。选择 **SW/SWD** 接口，时钟先用约400kHz（若无该档选较低档），确认能识别下载器及目标。不同版本ST-Link驱动菜单名称略有差异。
4. 在 **Utilities** 页面选择 **Use Target Driver for Flash Programming**，确认使用ST-Link；部分Keil版本显示 **Use Debug Driver**，选择复用上一步的调试驱动。
5. 在该驱动的 **Settings → Flash Download** 中添加适用于STM32F407的 **STM32F4xx Flash** 算法：起始地址 `0x08000000`，本型号可用Flash `0x80000`（512KB）。算法显示的覆盖范围可能更大，但必须支持该512KB型号。
6. 选 **Program、Verify、Reset and Run**，擦除选 **Erase Sectors**，确认保存。不要修改读保护/Option Bytes。需要保留原应用时先备份，下载新固件会覆盖原应用。

## 4. 烧录与观察

1. 再按一次F7，确认编译0错误；顶部Target仍是 **05_dual_sweep**。
2. 按 **F8 / Flash → Download**。观察下方输出，应显示编程、校验完成。
3. 若没有自动运行，按C30D复位键。打开两只舵机电源，观察两轴是否持续小幅往返；首个2秒等待可能已经在供电前经过。
4. 可选：电脑接C30D“串口1”Type-C，115200 8N1看日志，每200ms打印两路脉宽；不需要打开串口终端才能运动。

若只有一轴动：先关舵机电源，核对PC6/PC7信号、5V及共地。交换两只舵机的信号接口后再试，可判断问题跟随舵机/线束还是固定在某一路接口。若两轴都不动，先核对供电和实际烧录的Target，不要用手强拧通电舵机。

已编译文件：`outputs/firmware/05_dual_sweep.hex`、`.bin`；Keil自己编译的HEX/AXF位于 `work/uvision/05_dual_sweep/`。Keil的F8下载当前Target构建结果，不需要手动选另一个HEX。

## 本次验证

Keil/Arm Compiler6.7构建通过；实际扫动C模块已用主机测试检查两路输出一致、范围、速度、上下端点反转、2秒等待、主循环延迟不补大步、计时回绕。尚未在实物上下载或测量波形。
