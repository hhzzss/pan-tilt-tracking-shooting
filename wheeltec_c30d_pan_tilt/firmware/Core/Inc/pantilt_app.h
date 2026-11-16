#pragma once
#include <stdbool.h>
#include <stdint.h>
typedef struct {
    uint32_t rx_bytes, valid_frames, bad_lines, last_rx_ms;
    uint32_t centered_ms;
    int16_t ex, ey;
    uint16_t yaw_us, pitch_us;
    uint8_t found, tracking, relay_on;
} pt_debug_t;
extern volatile pt_debug_t pt_debug;
void pantilt_app_init(bool enable_pwm);
void pantilt_app_step(void);
void pantilt_on_uart_byte(uint8_t byte);
