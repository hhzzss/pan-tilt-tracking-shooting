#include "pantilt_config.h"
#include "pantilt_app.h"
#include "c30d_bsp.h"
#include "servo_single_test.h"
#include "servo_sweep_test.h"
#include "uart_protocol_test.h"
#include <stdio.h>
int main(void) {
#if PT_STAGE == 1 || PT_STAGE == 2
    c30d_servo_single_test_run_once();
#elif PT_STAGE == 3
    (void)c30d_uart_protocol_test_run();
#elif PT_STAGE == 5 || PT_STAGE == 6
    c30d_servo_sweep_init();
#elif PT_STAGE == 7
    c30d_bsp_init();
#else
    pantilt_app_init(true);
#endif
    c30d_bsp_log("\r\nC30D F407VET6 pan/tilt; UART1 log 115200 8N1\r\n");
#if PT_STAGE == 3
    c30d_bsp_log("UART_RX_PA3_V3: USART2 RX=PA3 AF7; rx=received bytes; PWM OFF\r\n");
#elif PT_STAGE == 4
    c30d_bsp_log("TRACKING_RELAY_PC12_V3: pitch=60..120deg; X-only center=+/-50 for 2s -> ON; off-center/lost/stale -> OFF\r\n");
#endif
    uint32_t last_step = c30d_bsp_millis();
#if PT_STAGE == 7
    uint8_t relay_on = 0U;
    c30d_bsp_log("RELAY_PC12_V1: LOW trigger, open drain; OFF 2s / ON 1s; PWM OFF\r\n");
#else
    uint32_t last_log = last_step;
#endif
#if PT_STAGE == 5 || PT_STAGE == 6
    uint16_t sweep_pulse = 1500U;
#if PT_STAGE == 6
    c30d_bsp_log("Pitch check PC7 only: hold 2s, then 1450..1550 us; PC6 PWM off\r\n");
#else
    c30d_bsp_log("DUAL_TEST_V2: PC6 yaw + PC7 pitch PWM ON; hold 2s, then 1400..1600 us\r\n");
#endif
#endif
    for (;;) {
        uint32_t now = c30d_bsp_millis();
#if PT_STAGE == 7
        if ((uint32_t)(now - last_step) >= (relay_on ? 1000U : 2000U)) {
            last_step = now;
            relay_on = relay_on ? 0U : 1U;
            c30d_bsp_set_relay(relay_on);
            c30d_bsp_log(relay_on ? "relay=ON PC12=LOW\r\n" :
                                   "relay=OFF PC12=RELEASED\r\n");
        }
#elif PT_STAGE == 5 || PT_STAGE == 6
        (void)last_step;
        sweep_pulse = c30d_servo_sweep_step();
#elif PT_STAGE >= 3
        if ((uint32_t)(now - last_step) >= PT_CONTROL_PERIOD_MS) {
            last_step = now;
            pantilt_app_step();
        }
#else
        (void)last_step;
#endif
#if PT_STAGE != 7
        if ((uint32_t)(now - last_log) >= 200U) {
            char text[224];
            last_log = now;
#if PT_STAGE == 6
            (void)snprintf(text, sizeof(text), "stage=6 pitch check PC7=%u us; PC6 PWM off\r\n",
                (unsigned)sweep_pulse);
#elif PT_STAGE == 5
            (void)snprintf(text, sizeof(text), "DUAL_TEST_V2 stage=5 PC6=%u PC7=%u us\r\n",
                (unsigned)sweep_pulse, (unsigned)sweep_pulse);
#elif PT_STAGE <= 2
            (void)snprintf(text, sizeof(text), "stage=%u axis=%s pulse=%u us\r\n",
                (unsigned)PT_STAGE, PT_STAGE == 1 ? "PC6 yaw" : "PC7 pitch",
                (unsigned)PT_TEST_PULSE_US);
#else
            (void)snprintf(text, sizeof(text),
                "stage=%u rx=%lu ok=%lu bad=%lu uart_err=%lu found=%u ex=%d ey=%d age=%lu active=%u pwm=%u/%u center_ms=%lu relay=%u\r\n",
                (unsigned)PT_STAGE, (unsigned long)pt_debug.rx_bytes,
                (unsigned long)pt_debug.valid_frames,
                (unsigned long)pt_debug.bad_lines, (unsigned long)c30d_uart_rx_errors,
                (unsigned)pt_debug.found, (int)pt_debug.ex, (int)pt_debug.ey,
                (unsigned long)(now - pt_debug.last_rx_ms), (unsigned)pt_debug.tracking,
                (unsigned)pt_debug.yaw_us, (unsigned)pt_debug.pitch_us,
                (unsigned long)pt_debug.centered_ms, (unsigned)pt_debug.relay_on);
#endif
            c30d_bsp_log(text);
        }
#endif
    }
}
