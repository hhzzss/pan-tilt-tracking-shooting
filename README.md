# 二维云台跟踪射击

完整项目包含 K230 检测、UART 目标偏差发送、C30D 双轴跟踪控制，以及接线、编译烧录和离线部署文档。

整理现有的 DshanPI CanMV-K230 V3 MicroPython 例程、目标检测部署脚本、模型配置和说明文档。原始代码中的作者及许可声明均予以保留；本仓库不是厂商资料全集，也不是完整 CanMV / EdgeOS SDK。

## 完整实验的运行入口

1. [完整项目与部署顺序](docs/完整实验项目.md)。
2. [C30D 固件、接线与编译入口](wheeltec_c30d_pan_tilt/README.md)。
3. [K230 sabo 模型部署](k230-stm32-tracking/outputs/sabo模型部署说明.md)。
4. [K230 电池独立运行 / SD 卡 main.py](k230-stm32-tracking/outputs/standalone/离线部署说明.md)。

## 从哪里开始

- [项目结构与运行说明](docs/项目说明.md)：运行环境、例程分类、两种模型目录和常见问题。
- [发布范围与资料来源](docs/发布范围与来源.md)：哪些文件被收录、哪些大型或第三方资料没有上传。
- [原文件清单与 SHA-256](docs/原文件清单.csv)：记录来源原件与发布副本的哈希；部分说明已将原绝对路径转换为仓库相对路径。

## 主要目录

| 路径 | 用途 |
| --- | --- |
| `CanMV_V3.0/04_MicroPython例程源码/` | 基础、摄像头、特征、颜色、AI、多媒体、网络等 MicroPython 实验 |
| `model/det_image.py` | 单张图片的模型部署例程 |
| `model/det_video.py` | 使用 Pipeline 和实体显示配置的视频检测例程 |
| `model/mp_deployment_source/` | sabo 检测模型与 JSON 配置 |
| `wheeltec_c30d_pan_tilt/` | C30D 固件源、Keil 工程、测试、接线与烧录说明 |
| `k230-stm32-tracking/outputs/` | 已适配 sabo 的 K230 串口跟踪与离线入口 |
| `docs/` | 项目解释、资料来源及文件清单 |

## 使用前须知

这些程序面向 K230 板端的 MicroPython/CanMV 环境，不能通过在普通电脑上 `pip install` 后直接运行。首次运行前，应准备匹配的固件、摄像头及 SD 卡资源。

`person_detection.py` 已被本地项目修改为 sabo 模型和串口跟踪版本，不能只根据旧文件名认定它仍在识别人。`model/det_video.py` 是另一种原始部署入口，不具备相同的摄像头、预览与跟踪配置，详见项目说明。

本次整理没有修改算法、接线或控制参数，也没有进行硬件运行验收。

## 许可与署名

不同文件按各自原有许可使用。CanMV 例程中存在 GPL v3 声明；Canaan 部署脚本保留原作者说明。不要把本仓库统一视为 MIT 或声称全部内容均为原创。[来源说明](docs/发布范围与来源.md)记录了具体范围。
