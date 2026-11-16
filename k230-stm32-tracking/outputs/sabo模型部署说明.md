# sabo 模型替换与上板步骤

已修改原文件：

`../..\CanMV_V3.0\04_MicroPython例程源码\06_AI视觉实验\01_人形处理\01-1_人形检测\person_detection.py`

本目录的 `person_detection.py` 是相同的部署副本。旧人形模型版本备份在：

`..\work\person_detection.before-sabo-model.py`

## 修改内容

参数取自用户提供的 `../..\model\mp_deployment_source\deploy_config.json`。

| 项目 | 修改前 | 修改后 |
| --- | --- | --- |
| 模型 | person_detect_yolov5n.kmodel | best_AnchorBaseDet_can2_5_s_20261020171350.kmodel |
| 板端模型路径 | /sdcard/examples/kmodel/person_detect_yolov5n.kmodel | /sdcard/model/mp_deployment_source/best_AnchorBaseDet_can2_5_s_20261020171350.kmodel |
| 模型输入 | 640×640 | 320×320 |
| 类别 | person | sabo（类别索引 0） |
| 置信度阈值 | 0.2 | 0.4 |
| NMS 阈值 | 0.6 | 0.5 |
| 锚框 | 通用人形模型锚框 | 本次训练配置的 18 个值 |
| letterbox 填充 | 黑色 0 | 配套 AnchorBaseDet 例程的灰色 114 |

锚框按部署脚本顺序展平：

```text
61,132,76,153,102,142,
96,182,105,201,120,190,
113,238,132,255,166,260
```

保留 `aicube.anchorbasedet_post_process` 三输出后处理、步长 [8,16,32] 和 nms_option=False。修正了右侧 padding 在奇数时的舍入；当前 640×480 → 320×320 的上下 padding 为 40/40，左右为 0/0。

摄像头仍为 CSI0，采集与预览仍为 640×480。计算 ex/ey 继续使用后处理映射回 640×480 的目标坐标，以各轴半幅归一化。串口协议和 C30D 控制固件无需因为更换模型而修改。

## SD 卡上放置文件

把电脑上的整个文件夹：

`../..\model\mp_deployment_source`

复制到 K230 的 SD 卡 `model` 文件夹下，形成：

```text
/sdcard/
  model/
    mp_deployment_source/
      best_AnchorBaseDet_can2_5_s_20261020171350.kmodel
      deploy_config.json
```

本脚本已将 JSON 中相关配置写入代码，不会在运行时读取 JSON；将 JSON 一起保留用于核对。电脑 E: 路径不能直接供 K230 使用，必须实际复制模型到 SD 卡。

在 CanMV IDE 重新打开修改后的 `person_detection.py` 并运行，确认打印的模型路径是上述 sabo 模型，随后出现首次推理成功日志。也可以把脚本保存到 `/sdcard/main.py` 用于开机自启；本次修改无需重新烧录 CanMV 固件。

不要直接运行 `model/det_video.py` 来替代本脚本：那个原始部署例程使用默认 Pipeline/实体显示配置，没有当前已适配的 CSI0 + IDE 预览和 C30D 串口发送功能。

## C30D 联调

C30D 使用已经准备好的 `04_tracking_PA3.hex`，K230 IO44 → C30D PA3，GND → GND。协议继续为 115200 8N1、`$T,found,ex,ey\n`，偏差范围 -1000～1000、右/下为正，丢失目标发 `$T,0,0,0\n`。

预览应显示 sabo 框、目标中心、画面中心和 dx/dy；目标移到右/下时相应偏差为正。当前只会根据新模型的类别 sabo 跟踪，不再使用人形模型识别人。多个同类别目标时选择当前面积最大者。

发送节流仍为 50ms，实际速度受模型推理耗时影响；C30D 默认 300ms 超时，需实测新的完整有效帧间隔小于 300ms，并观察转动后偏差是否减小。

## 检查结果与限制

已通过 PC 语法检查、与真实 JSON 的参数一致性检查、预处理/后处理调用检查，以及原有 UART、目标误差、绘制、超时发送间隔与资源清理模拟检查。

尚未实机验证本模型加载、识别准确率和完整处理帧率。该模型配置标注 nncase_version=2.11.0；PC 上的检查不能证明板载运行时一定兼容。若板端停在 model load 或 inference/postprocess 阶段，请保留完整错误日志，以确定是否为模型运行时兼容问题。
