"""Build the MDK Arm Compiler 6 targets without opening uVision."""
import argparse
import os
import shutil
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--tools', default=os.environ.get('C30D_ARM_TOOLS', r'C:\Keil_v5\ARM\ARMCLANG\bin'))
parser.add_argument('--stage', type=int, choices=range(1, 8))
args = parser.parse_args()
tools = Path(args.tools)
for name in ('armclang.exe', 'armasm.exe', 'armlink.exe', 'fromelf.exe'):
    if not (tools / name).is_file():
        sys.exit('Missing ' + str(tools / name) + '; install MDK Arm Compiler 6 or pass --tools')
include = ['Core/Inc', 'BSP', 'Stages', 'Vendor/CMSIS/Include', 'Vendor/Device/Include']
sources = ['Core/Src/main.c', 'Core/Src/pantilt_protocol.c',
           'Core/Src/pantilt_controller.c', 'Core/Src/pantilt_app.c',
           'BSP/c30d_bsp_stm32f407.c', 'Stages/servo_single_test.c',
           'Stages/uart_protocol_test.c', 'Stages/servo_sweep_test.c',
           'Vendor/Device/Source/system_stm32f4xx.c']
stages = {1: '01_yaw_center', 2: '02_pitch_center', 3: '03_uart_monitor',
          4: '04_tracking', 5: '05_dual_sweep', 6: '06_pitch_sweep',
          7: '07_relay_pc12_test'}

def run(command, log):
    result = subprocess.run([str(x) for x in command], cwd=root,
                            capture_output=True, text=True, errors='replace')
    log.write('$ ' + subprocess.list2cmdline([str(x) for x in command]) + '\n')
    log.write(result.stdout + result.stderr)
    if result.returncode:
        print(result.stdout + result.stderr)
        raise RuntimeError('Command failed: ' + str(command[0]))

for stage, name in stages.items():
    if args.stage and stage != args.stage:
        continue
    out = root.parent / 'work' / 'build' / name
    final = root.parent / 'outputs' / 'firmware'
    out.mkdir(parents=True, exist_ok=True)
    final.mkdir(parents=True, exist_ok=True)
    with (out / 'build.log').open('w', encoding='utf-8') as log:
        objects = []
        for source in sources:
            obj = out / (Path(source).stem + '.o')
            command = [tools / 'armclang.exe', '--target=arm-arm-none-eabi',
                       '-mcpu=cortex-m4', '-mfpu=fpv4-sp-d16', '-mfloat-abi=hard',
                       '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                       '-DSTM32F407xx', '-DPT_STAGE=' + str(stage)]
            command.extend('-I' + path for path in include)
            run(command + ['-c', source, '-o', obj], log)
            objects.append(obj)
        startup = out / 'startup_stm32f407xx.o'
        run([tools / 'armasm.exe', '--cpu=Cortex-M4', '--fpu=FPv4-SP', '-g',
             'Vendor/Device/Source/startup_stm32f407xx.s', '-o', startup], log)
        objects.append(startup)
        axf = out / (name + '.axf')
        run([tools / 'armlink.exe', '--cpu=Cortex-M4', '--fpu=FPv4-SP',
             '--libpath=' + str(tools.parent / 'lib'),
             '--scatter=C30D.sct', '--map', '--symbols', '--info=sizes',
             '--list=' + str(out / (name + '.map')), '-o', axf] + objects, log)
        run([tools / 'fromelf.exe', '--i32combined', '--output=' + str(final / (name + '.hex')), axf], log)
        run([tools / 'fromelf.exe', '--bin', '--output=' + str(final / (name + '.bin')), axf], log)
    if stage in (3, 4):
        shutil.copyfile(final / (name + '.hex'), final / (name + '_PA3.hex'))
    print(name + ': PASS')
