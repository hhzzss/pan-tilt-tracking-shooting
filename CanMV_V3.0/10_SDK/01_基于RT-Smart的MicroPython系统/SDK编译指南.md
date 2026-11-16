# 在 CanMV-K230 完整源码包中编译 EdgeOS 固件

本文说明如何从本目录直接编译适用于 **DshanPI CanMV-K230 V3** 的
EdgeOS Desktop 固件。

这是一份已经集成完成的 SDK 源码包，当前版本信息如下：

| 项目 | 当前值 |
| --- | --- |
| 产品配置 | `k230_canmv_dongshanpi_edgeos_defconfig` |
| SDK 适配集 | `edgeos-sdk-v1.0.2`（包内标识 `edgeos_sdk_v1_0_2`） |
| EdgeOS 产品版本 | `v0.7.7` |
| 完整固件 | `DshanPI_EdgeOS_Desktop_v0.7.7.img` |
| 目标存储 | DshanPI CanMV-K230 V3 板载 eMMC |

SDK 适配、EdgeOS Desktop、模型、字体和板级配置均已包含。使用本源码包时：

- 不需要执行 `repo init` 或 `repo sync`；
- 不需要另外克隆或复制 `EdgeOS_Desktop`；
- 不需要执行 `git lfs pull`；
- 不需要再次运行 SDK 补丁或集成脚本；
- 不要把本应用单独复制到另一个、版本不明的 SDK 中编译。

> 本包包含完整源码，但工具链默认不包含在工程目录内。新主机首次执行
> `make dl_toolchain` 时需要联网；主机依赖已经安装且两套 K230 工具链已经
> 预装时，可以离线编译。

> 本指南是当前 `v0.7.7` 完整源码包的编译依据。应用子目录中的
> `docs/BUILD_RTOS_K230.md` 面向从 Git/repo 组装较早版本 SDK，不适用于本包；
> 本包也不要运行其中依赖 Git 元数据和旧版本号的 `check_sdk_compat.sh`。

## 1. 快速编译

已经安装主机依赖时，在 SDK 根目录执行：

```bash
cd /path/to/canmv_k230

# 新主机首次执行，下载 RT-Smart musl 和 U-Boot glibc 两套工具链
make dl_toolchain

# 选择 DshanPI EdgeOS 专用产品配置
make k230_canmv_dongshanpi_edgeos_defconfig

# 全量编译并保留日志；pipefail 可确保 make 失败时命令返回非 0
bash -o pipefail -c \
  'time make -j"$(nproc)" 2>&1 | tee edgeos-v0.7.7-build.log'
```

编译成功后验证完整镜像：

```bash
OUT=output/k230_canmv_dongshanpi_edgeos_defconfig
IMAGE="$OUT/DshanPI_EdgeOS_Desktop_v0.7.7.img"

test -s "$IMAGE"
python3 src/applications/EdgeOS_Desktop/tools/check_firmware_image.py \
  "$IMAGE"
```

检查器必须返回 0，并以这行结束：

```text
PASS: EdgeOS firmware image is structurally valid.
```

## 2. 编译主机要求

推荐环境：

- Ubuntu 20.04 或 22.04 x86_64；
- 建议 16 GiB 或更多内存；内存较小时把并行度改为 `-j4`；
- 建议在解压源码后仍保留至少 25 GiB 可用空间；源码、工具链和构建输出
  合计建议准备 40 GiB 以上空间；
- 源码路径尽量只使用 ASCII 字符，且不要包含空格。

安装依赖：

```bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  make autoconf automake bison flex gcc g++ gawk libncurses5-dev \
  pkg-config libconfuse-dev libssl-dev python3 python3-pip \
  python-is-python3 cmake libyaml-dev scons mtools bzip2 curl git \
  openssh-client rsync dosfstools ca-certificates wget fdisk

pip3 install pycryptodome gmssl scons==3.1.2
```

`repo` 和 Git LFS 不是完整源码包的编译依赖，不要按普通 CanMV SDK 的同步流程
重新拉取或覆盖本目录。

## 3. 编译前检查源码包

在 SDK 根目录执行：

```bash
test -s SOURCE_PACKAGE_INFO
test -s configs/k230_canmv_dongshanpi_edgeos_defconfig
test -s boards/k230_canmv_dongshanpi/system-version.txt
test -s src/applications/EdgeOS_Desktop/Kconfig
test -s src/applications/EdgeOS_Desktop/third_party/vaxp/include/vaxp_commands.h
test -s src/rtsmart/mpp/middleware/src/mp4_player/include/kplayer.h
test -s src/applications/EdgeOS_Desktop/tools/check_firmware_image.py

grep -Fq \
  'subdirs-$(CONFIG_APP_ENABLE_EDGEOS_DESKTOP) += EdgeOS_Desktop' \
  src/applications/apps.mk
grep -Fx 'v0.7.7' boards/k230_canmv_dongshanpi/system-version.txt
```

全部命令都应返回 0。`SOURCE_PACKAGE_INFO` 是去除 `.repo` 和 `.git` 后的
源码版本记录，最终打包会读取它生成 `revision.txt`；不要删除、置空或随意修改。

如果上述文件缺失，请重新获取完整源码包。不要从其他 SDK 临时复制单个头文件，
否则很容易得到“可以编译但接口 ABI 或固件布局不一致”的混合工程。

## 4. 准备工具链

默认工具链目录为：

```text
$HOME/.kendryte/k230_toolchains
```

首次执行：

```bash
make dl_toolchain
```

该命令会下载两套工具链：

- RT-Smart/EdgeOS 使用的 RISC-V musl 工具链；
- U-Boot 使用的 Xuantie RISC-V glibc 工具链。

不要只下载其中一套。可用以下命令检查：

```bash
RTSMART_TOOLCHAIN_BIN="${HOME}/.kendryte/k230_toolchains/riscv64-linux-musleabi_for_x86_64-pc-linux-gnu/bin"
UBOOT_TOOLCHAIN_BIN="${HOME}/.kendryte/k230_toolchains/Xuantie-900-gcc-linux-5.10.4-glibc-x86_64-V2.6.0/bin"

test -x "$RTSMART_TOOLCHAIN_BIN/riscv64-unknown-linux-musl-gcc"
test -x "$UBOOT_TOOLCHAIN_BIN/riscv64-unknown-linux-gnu-gcc"
```

如果工具链需要放到其他位置，必须在同一个终端中同时设置两个变量：

```bash
export SDK_TOOLCHAIN_DIR="$HOME/k230_toolchains"
export K230_TOOLCHAIN_BIN="$SDK_TOOLCHAIN_DIR/riscv64-linux-musleabi_for_x86_64-pc-linux-gnu/bin"

make dl_toolchain
```

顶层 SDK 使用 `SDK_TOOLCHAIN_DIR`，多个 EdgeOS 子应用使用
`K230_TOOLCHAIN_BIN`。只设置其中一个会导致部分组件找不到交叉编译器。

## 5. 选择 EdgeOS 产品配置

执行：

```bash
make list-def | grep -F k230_canmv_dongshanpi_edgeos_defconfig
make k230_canmv_dongshanpi_edgeos_defconfig
```

终端应出现：

```text
Apply k230_canmv_dongshanpi_edgeos_defconfig success
```

再检查实际生效的配置：

```bash
grep -Fx \
  'CONFIG_BOARD_CONFIG_NAME="k230_canmv_dongshanpi_edgeos_defconfig"' \
  .config
grep -Fx 'CONFIG_APP_ENABLE_EDGEOS_DESKTOP=y' .config
grep -Fx 'CONFIG_RT_PARTITION_NUMBER=4' .config
```

专用 defconfig 已经启用 EdgeOS Desktop，不需要先运行 `make menuconfig`。
如果只是想查看菜单，EdgeOS 应位于 `Applications Configuration`；退出菜单后
建议重新执行专用 defconfig，避免保存了无意的配置变化。

## 6. 正式全量编译

推荐命令：

```bash
bash -o pipefail -c \
  'time make -j"$(nproc)" 2>&1 | tee edgeos-v0.7.7-build.log'
```

内存不足时降低并行度，例如：

```bash
bash -o pipefail -c \
  'time make -j4 2>&1 | tee edgeos-v0.7.7-build.log'
```

构建过程中出现下面这行，说明 EdgeOS 应用已经进入构建链：

```text
[BUILD] applications EdgeOS_Desktop
```

正式成功必须同时满足：

1. 上述全量构建命令退出码为 0；
2. 日志末尾出现：

```text
Build K230 done, board k230_canmv_dongshanpi, config k230_canmv_dongshanpi_edgeos_defconfig
```

不要把 `make app` 当成最终验收：它只适合诊断应用组件，不会生成最终固件。
也不建议用 SDK 自带的 `make log` 做发布验收，因为其内部 `make | tee` 没有
启用 `pipefail`，某些内部编译失败可能被 `tee` 的退出码掩盖。

## 7. 产物说明与校验

所有正式产物位于：

```text
output/k230_canmv_dongshanpi_edgeos_defconfig/
```

主要文件如下：

| 文件 | 用途 | 能否用于 LYNX 首次烧录 |
| --- | --- | --- |
| `DshanPI_EdgeOS_Desktop_v0.7.7.img` | 包含 MBR、TOC、SPL、U-Boot、RT-Smart 与应用分区的完整出厂/恢复镜像 | **可以** |
| `DshanPI_EdgeOS_Desktop_v0.7.7.img.gz` | 完整 IMG 的压缩传输文件 | 先解压，不能直接烧录 |
| `DshanPI_EdgeOS_Desktop_v0.7.7_ota.kdimg` | 已运行 EdgeOS 的 A/B OTA 更新包 | **禁止** |
| `DshanPI_EdgeOS_Desktop_v0.7.7_ota.kdimg.gz` | OTA 包的压缩传输文件 | **禁止** |

完整 IMG 应包含约 20 MiB 的 `bin`、1 GiB 的 `app_a` 和 1 GiB 的
`app_b` 三个预创建 FAT 分区。执行完整验收：

```bash
OUT=output/k230_canmv_dongshanpi_edgeos_defconfig
IMAGE="$OUT/DshanPI_EdgeOS_Desktop_v0.7.7.img"
OTA="$OUT/DshanPI_EdgeOS_Desktop_v0.7.7_ota.kdimg"

test -s "$IMAGE"
test -s "$OTA"

python3 src/applications/EdgeOS_Desktop/tools/check_firmware_image.py \
  "$IMAGE"

fdisk -l "$IMAGE"
sha256sum "$IMAGE" "$OTA"
sed -n '1,120p' "$OUT/images/sdcard/revision.txt"
```

固件检查器会验证 MBR、11 个 K230 TOC 条目、A/B 分区布局以及内部负载摘要。
只要没有得到 `PASS`，就不要烧录或分发镜像。

每次构建会把构建时间和源码版本写入镜像，因此不同主机或不同时间生成的
SHA-256 可能不同。验收时不要写死历史哈希；应保存本次构建的哈希，并以全量
构建退出码 0 和结构检查器通过为准。

## 8. 增量编译和完全重编

只修改 EdgeOS 源码后，可以直接增量编译：

```bash
make -j"$(nproc)"
```

`make clean` 会清理多个组件对象，但可能保留顶层旧的 `.img`、`.kdimg` 和
压缩文件。构建失败后不要把这些旧文件误认为本次新产物。

发布前或怀疑旧对象污染时，建议完整清理并重编：

```bash
make distclean
make k230_canmv_dongshanpi_edgeos_defconfig
bash -o pipefail -c \
  'time make -j"$(nproc)" 2>&1 | tee edgeos-v0.7.7-build.log'
```

`make distclean` 会删除当前配置对应的整个输出目录以及 `.config`，所以之后必须
重新执行专用 defconfig。同一份源码目录也不要同时启动两个构建，它们会共用
`.config` 和 `output/`。

## 9. 使用 LYNX 烧录

首次安装、恢复或完整重刷时使用：

| LYNX 选项 | 设置 |
| --- | --- |
| 芯片 | `K230` |
| 目标介质 | `EMMC` / K230 `SDIO0` |
| 文件 | 未压缩的完整 `DshanPI_EdgeOS_Desktop_v0.7.7.img` |
| 写入地址/偏移 | `0x0` |

建议烧录前拔出 TF 卡，避免系统从其他介质启动。不能从 `0xe0000`、
`0x100000` 等镜像内部地址开始写，也不能把 `_ota.kdimg` 当作完整固件。

设备首次从 eMMC 启动时会利用剩余空间创建第 4 个 `/data` 分区，并可能自动
重启一次以重新扫描分区表；在此期间不要断电。

串口若先看到 `HS200 tuning failed: -110`，随后成功回退到
`MMC High Speed (52MHz)`，通常不是致命错误，应继续查看后续第一条真实错误。

## 10. 常见问题

| 现象 | 原因与处理 |
| --- | --- |
| 找不到 `riscv64-unknown-linux-musl-gcc` 或 `riscv64-unknown-linux-gnu-gcc` | 运行 `make dl_toolchain`；非默认目录必须同时设置 `SDK_TOOLCHAIN_DIR` 和 `K230_TOOLCHAIN_BIN` |
| `Applications Configuration` 中没有 EdgeOS | 确认使用本包并检查 `src/applications/EdgeOS_Desktop/Kconfig`、`src/applications/apps.mk`；失败说明源码包不完整，不要临时复制应用 |
| `vaxp_commands.h` 不存在 | 完整包应包含 `src/applications/EdgeOS_Desktop/third_party/vaxp/include/vaxp_commands.h`；重新获取完整包 |
| `fatal error: kplayer.h: No such file or directory` | SDK 补丁集缺失或混用了其他 SDK；完整包应包含 `src/rtsmart/mpp/middleware/src/mp4_player/include/kplayer.h` |
| 缺少 `lv_k230_touch_accept_click()`、`k230_ota_get_status()` 等接口 | SDK 版本或补丁集不匹配；不要逐个补符号，重新解压并使用完整源码包 |
| `Missing .repo metadata and SOURCE_PACKAGE_INFO` | 完整源码包缺少根目录 `SOURCE_PACKAGE_INFO`；恢复该包的原始文件 |
| `Repo metadata is present but the repo command is unavailable` | 当前目录仍保留隐藏的 `.repo`；安装 `repo`，或使用正式发布的去元数据完整源码包。不要只删除部分 `.repo` 内容 |
| Python 报缺少 `Crypto`、`gmssl` 或 SCons | 执行 `pip3 install pycryptodome gmssl scons==3.1.2` |
| `No space left on device` 或 FAT/genimage 空间不足 | 清理磁盘并确认使用本包的 1 GiB A/B 产品布局；建议构建前保留至少 25 GiB 空间 |
| 编译进程被系统杀死 | 通常是内存不足；降低为 `make -j4`，必要时增加 swap |
| `K230 boot: invalid TOC entry 1` | 停止使用该镜像；先让 `check_firmware_image.py` 通过，再用完整 `.img`、EMMC/SDIO0、偏移 `0x0` 重新烧录 |
| LYNX 显示成功但开发板不启动 | 检查是否误用了 OTA/GZ 文件、介质或偏移；拔出 TF 卡后用未压缩完整 IMG 重刷 |

## 11. 发布前最小验收清单

- 使用 `k230_canmv_dongshanpi_edgeos_defconfig`；
- 全量 `make` 返回 0；
- 日志包含 `[BUILD] applications EdgeOS_Desktop`；
- 日志末尾包含 `Build K230 done ...`；
- `DshanPI_EdgeOS_Desktop_v0.7.7.img` 非空；
- `check_firmware_image.py` 返回 0 并输出 `PASS`；
- 保存本次 IMG 和 OTA 的 SHA-256；
- 在真实 DshanPI CanMV-K230 V3 上完成一次 LYNX/eMMC 启动验收；
- 确认显示、触摸、摄像头、Wi-Fi、音频和 EdgeOS Desktop 均正常。

只有完成板端验收，才能说明固件不仅“编译成功”，而且可以正常启动和使用。
