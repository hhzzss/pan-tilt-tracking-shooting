import os
import sys

def check_module(name):
    try:
        __import__(name)
        print("[OK] 模块:", name)
    except Exception as e:
        print("[FAIL] 模块:", name, repr(e))
        sys.print_exception(e)

check_module("nncase_runtime")
check_module("aicube")
check_module("ulab.numpy")
check_module("libs.PipeLine")
check_module("libs.AIBase")
check_module("libs.AI2D")

model = "/sdcard/examples/kmodel/person_detect_yolov5n.kmodel"
try:
    info = os.stat(model)
    print("[OK] 模型文件，字节数:", info[6])
except Exception as e:
    print("[FAIL] 模型文件:", model, repr(e))
