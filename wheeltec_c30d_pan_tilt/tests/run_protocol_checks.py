"""Dependency-free test entry; also works with pytest test_protocol.py."""
import test_protocol
for name in sorted(dir(test_protocol)):
    if name.startswith("test_"):
        getattr(test_protocol, name)()
        print(name + ": PASS")
