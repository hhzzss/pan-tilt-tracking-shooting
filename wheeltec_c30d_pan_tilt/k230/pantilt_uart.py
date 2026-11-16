"""DshanPI CanMV V3 UART2 -> C30D. Boxes: [class, score, x1,y1,x2,y2]."""

def send_packet(uart, found, ex=0, ey=0):
    packet = ("$T,%d,%d,%d\n" % (int(bool(found)), ex, ey)).encode("ascii")
    if uart.write(packet) != len(packet):
        raise OSError("UART tracking frame write incomplete")


def send_detection(uart, detections, width, height, target_class=None):
    """Select the largest visible box; right/down errors are positive.

    Coordinates must already be mapped to the original image, not letterbox
    model coordinates. Set target_class to your doll model's class index.
    """
    if width <= 0 or height <= 0:
        raise ValueError("image width and height must be positive")
    best = None
    best_area = 0
    if detections is not None:
        for box in detections:
            if target_class is not None and int(box[0]) != target_class:
                continue
            x1, y1 = max(0, min(width, float(box[2]))), max(0, min(height, float(box[3])))
            x2, y2 = max(0, min(width, float(box[4]))), max(0, min(height, float(box[5])))
            area = (x2 - x1) * (y2 - y1) if x2 > x1 and y2 > y1 else 0
            if area > best_area:
                best, best_area = (x1, y1, x2, y2), area
    if best is None:
        send_packet(uart, False)
        return
    ex = int(round(((best[0] + best[2]) * 0.5 - width * 0.5) * 2000 / width))
    ey = int(round(((best[1] + best[3]) * 0.5 - height * 0.5) * 2000 / height))
    send_packet(uart, True, ex, ey)


def setup_uart(machine_uart, fpioa):
    """Fixed to the verified V3 J6: pin2 TX IO44, pin3 RX IO45."""
    fpioa.set_function(44, fpioa.UART2_TXD)
    fpioa.set_function(45, fpioa.UART2_RXD)
    return machine_uart(machine_uart.UART2, baudrate=115200,
                        bits=machine_uart.EIGHTBITS,
                        parity=machine_uart.PARITY_NONE,
                        stop=machine_uart.STOPBITS_ONE)
