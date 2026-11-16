/* Stage 5 sweeps both axes; stage 6 checks pitch alone without yaw PWM. */
#include "servo_sweep_test.h"
#include "pantilt_config.h"
#include "c30d_bsp.h"
#include <stdbool.h>
static uint16_t pulse;
static bool increasing, started;
static uint32_t start_ms, last_step_ms;
void c30d_servo_sweep_init(void) {
    c30d_bsp_init();
    pulse = 1500U;
    increasing = true;
    started = false;
    start_ms = last_step_ms = c30d_bsp_millis();
#if PT_STAGE == 6
    c30d_bsp_enable_pwm(C30D_PWM_PITCH, 1500U, pulse);
#else
    c30d_bsp_enable_pwm(C30D_PWM_YAW | C30D_PWM_PITCH, pulse, pulse);
#endif
}
uint16_t c30d_servo_sweep_step(void) {
    uint32_t now = c30d_bsp_millis();
    if (!started) {
        if ((uint32_t)(now - start_ms) < PT_SWEEP_START_HOLD_MS) return pulse;
        started = true;
        last_step_ms = now;
    }
    if ((uint32_t)(now - last_step_ms) < PT_CONTROL_PERIOD_MS) return pulse;
    last_step_ms = now; /* Never catch up a delayed loop with a large move. */
    if (increasing) {
        unsigned next = pulse + PT_SWEEP_STEP_US;
        pulse = (uint16_t)(next >= PT_SWEEP_MAX_US ? PT_SWEEP_MAX_US : next);
        if (pulse == PT_SWEEP_MAX_US) increasing = false;
    } else {
        int next = (int)pulse - (int)PT_SWEEP_STEP_US;
        pulse = (uint16_t)(next <= (int)PT_SWEEP_MIN_US ? PT_SWEEP_MIN_US : next);
        if (pulse == PT_SWEEP_MIN_US) increasing = true;
    }
#if PT_STAGE != 6
    c30d_bsp_set_yaw_pulse_us(pulse);
#endif
    c30d_bsp_set_pitch_pulse_us(pulse);
    return pulse;
}
