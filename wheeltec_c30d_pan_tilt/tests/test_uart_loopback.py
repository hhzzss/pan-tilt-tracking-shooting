"""Exercise the diagnostic with split echoes, no echo, wrong data, short writes."""
import contextlib
import importlib.util
import io
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "uart_loopback_test", Path(__file__).parents[1] / "k230/uart_loopback_test.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class Clock:
    def __init__(self): self.ms = 0
    def ticks_ms(self): return self.ms
    def ticks_diff(self, a, b): return a - b
    def sleep_ms(self, ms): self.ms += ms


class Uart:
    def __init__(self, mode): self.mode, self.chunks = mode, []
    def write(self, packet):
        if self.mode == "short": return len(packet) - 1
        if self.mode == "echo": self.chunks = [packet[:3], packet[3:]]
        if self.mode == "wrong": self.chunks = [b"X" * len(packet)]
        return len(packet)
    def read(self): return self.chunks.pop(0) if self.chunks else None


def main():
    for mode, expected in (("echo", 10), ("none", 0), ("wrong", 0)):
        clock = Clock()
        with contextlib.redirect_stdout(io.StringIO()):
            assert mod.check_loopback(Uart(mode), clock) == expected
        if mode == "none": assert clock.ms == 4000
    try:
        mod.check_loopback(Uart("short"), Clock())
    except OSError:
        pass
    else:
        raise AssertionError("short writes must fail")
    print("K230 loopback diagnostic split/missing/corrupt echoes and short writes: PASS")


if __name__ == "__main__":
    main()
