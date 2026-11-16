# 已随工程包含的依赖

- CMSIS Core：本机 Keil ARM.CMSIS 5.4.0 包中 Include 文件，Apache-2.0；许可见 CMSIS/LICENSE.txt，保留各文件原版权。
- STM32F4 device CMSIS：STMicroelectronics 的 `cmsis-device-f4` 仓库 master，2026-10-20 获取；Include 内 stm32f407xx.h、stm32f4xx.h、system_stm32f4xx.h，以及 Source 内 system_stm32f4xx.c、ARM 启动文件 startup_stm32f407xx.s。许可见 Device/LICENSE.md。
- 上游：https://github.com/STMicroelectronics/cmsis-device-f4 ，原始启动文件在 Source/Templates/arm/。
- 本地唯一的启动文件改动：Stack_Size 从 0x400 增至 0x1000，并添加说明。

工程不依赖 CubeMX 生成代码或另装 HAL。使用 CMSIS 寄存器定义，系统时钟由 BSP 选择内部 HSI 16MHz；上游文件中的 HSE 默认常量没有用于本工程的时钟配置。
