import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "pantilt_uart", Path(__file__).parents[1] / "k230" / "pantilt_uart.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class FakeUart:
    def __init__(self): self.data = []
    def write(self, data): self.data.append(data); return len(data)

def test_normalized_center_and_clamping():
    u = FakeUart()
    mod.send_detection(u, [[0, 0.9, 0, 0, 640, 480]], 640, 480)
    assert u.data[-1] == b"$T,1,0,0\n"
    mod.send_detection(u, [[0, 0.9, 600, 0, 700, 480]], 640, 480)
    assert u.data[-1] == b"$T,1,938,0\n"

def test_lost_target():
    u = FakeUart()
    mod.send_detection(u, [], 640, 480)
    assert u.data[-1] == b"$T,0,0,0\n"

def test_largest_visible_target_and_class_filter():
    u = FakeUart()
    mod.send_detection(u, [
        [0, 0.25, 0, 0, 100, 100],
        [0, 0.90, 480, 0, 640, 480],
    ], 640, 480)
    assert u.data[-1] == b"$T,1,750,0\n"
    mod.send_detection(u, [[1, .99, 0, 0, 640, 480], [0, .4, 480, 0, 640, 480]], 640, 480, 0)
    assert u.data[-1] == b"$T,1,750,0\n"
    mod.send_detection(u, [[0, .99, 700, 0, 800, 480]], 640, 480)
    assert u.data[-1] == b"$T,0,0,0\n"

def test_invalid_image_and_short_write():
    try:
        mod.send_detection(FakeUart(), [], 0, 480)
        assert False
    except ValueError:
        pass
    class ShortUart:
        def write(self, data): return 1
    try:
        mod.send_detection(ShortUart(), [], 640, 480)
        assert False
    except OSError:
        pass
