"""Build and execute the actual C modules on Windows using installed MSVC."""
from pathlib import Path
import os
import subprocess
import sys
root = Path(__file__).resolve().parents[1]
vcvars = Path(os.environ.get('C30D_VCVARS', r'E:\VSBuildTools\App\VC\Auxiliary\Build\vcvars64.bat'))
out = root / 'work' / 'host_tests'
out.mkdir(parents=True, exist_ok=True)
tests = {
    'test_control': [root/'tests/test_control.c'] + [root/'firmware/Core/Src'/s for s in
        ('pantilt_protocol.c', 'pantilt_controller.c', 'pantilt_app.c')],
    'test_sweep': [root/'tests/test_sweep.c',root/'firmware/Stages/servo_sweep_test.c'],
    'test_pitch_sweep': [root/'tests/test_sweep.c',root/'firmware/Stages/servo_sweep_test.c'],
    'test_relay': [root/'tests/test_relay.c'],
}
includes = [root/'firmware/Core/Inc', root/'firmware/BSP', root/'firmware/Stages']
script = out/'run.cmd'
content = '@echo off\ncall "'+str(vcvars)+'" >nul\nif errorlevel 1 exit /b 1\n'
for name,sources in tests.items():
    command = ['cl', '/nologo', '/W4', '/WX', '/std:c11', '/D_CRT_SECURE_NO_WARNINGS']
    if name in ('test_sweep', 'test_pitch_sweep'):
        command += ['/DPT_STAGE='+('6' if name=='test_pitch_sweep' else '5')]
    if name == 'test_relay':
        command += ['/DPT_STAGE=7']
    command += ['/I'+str(x) for x in includes] + [str(x) for x in sources]
    command += ['/Fe:'+str(out/(name+'.exe'))]
    content += subprocess.list2cmdline(command)+'\nif errorlevel 1 exit /b 1\n'
    content += '"'+str(out/(name+'.exe'))+'"\nif errorlevel 1 exit /b 1\n'
script.write_text(content, encoding='utf-8')
sys.exit(subprocess.run(['cmd','/c',str(script)],cwd=out).returncode)
