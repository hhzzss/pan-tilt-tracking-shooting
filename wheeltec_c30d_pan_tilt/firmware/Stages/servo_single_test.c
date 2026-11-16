#include "servo_single_test.h"
#include "c30d_bsp.h"
#include "pantilt_config.h"
void c30d_servo_single_test_run_once(void) {
    c30d_bsp_init();
#if PT_STAGE == 1
    c30d_bsp_enable_pwm(C30D_PWM_YAW, PT_TEST_PULSE_US, 1500U);
#elif PT_STAGE == 2
    c30d_bsp_enable_pwm(C30D_PWM_PITCH, 1500U, PT_TEST_PULSE_US);
#endif
}
