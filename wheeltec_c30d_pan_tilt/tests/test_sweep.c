#include "servo_sweep_test.h"
#include "pantilt_config.h"
#include "c30d_bsp.h"
#include <assert.h>
#include <stdio.h>
static uint32_t now;
static uint16_t yaw, pitch;
static unsigned writes;
#if PT_STAGE == 6
#define EXPECT_OUTPUT(us) assert(yaw==1500 && pitch==(us))
#else
#define EXPECT_OUTPUT(us) assert(yaw==(us) && pitch==(us))
#endif
void c30d_bsp_init(void) { writes=0; }
uint32_t c30d_bsp_millis(void) { return now; }
void c30d_bsp_enable_pwm(uint8_t axes, uint16_t y, uint16_t p) {
#if PT_STAGE == 6
    assert(axes==C30D_PWM_PITCH);
#else
    assert(axes==(C30D_PWM_YAW|C30D_PWM_PITCH));
#endif
    yaw=y; pitch=p;
}
void c30d_bsp_set_yaw_pulse_us(uint16_t us) {
#if PT_STAGE == 6
    assert(!"Pitch-only check must not update yaw");
#endif
    yaw=us; ++writes;
}
void c30d_bsp_set_pitch_pulse_us(uint16_t us) { pitch=us; ++writes; }
int main(void) {
    now=0; c30d_servo_sweep_init(); assert(yaw==1500 && pitch==1500);
    now=1999; assert(c30d_servo_sweep_step()==1500 && writes==0);
    now=2000; assert(c30d_servo_sweep_step()==1500 && writes==0);
    now=2019; assert(c30d_servo_sweep_step()==1500);
    now=2020; assert(c30d_servo_sweep_step()==1501); EXPECT_OUTPUT(1501);
    now=3000; assert(c30d_servo_sweep_step()==1502); /* delayed loop only one step */
    unsigned low=0, high=0;
    for(unsigned i=0;i<2000;++i) {
        uint16_t previous=pitch; now+=20; uint16_t us=c30d_servo_sweep_step();
        EXPECT_OUTPUT(us); assert(us>=PT_SWEEP_MIN_US && us<=PT_SWEEP_MAX_US);
        int delta=(int)us-(int)previous; assert(delta==1 || delta==-1);
        if(us==PT_SWEEP_MIN_US) ++low;
        if(us==PT_SWEEP_MAX_US) ++high;
    }
    assert(low>=4 && high>=4);
    now=0xfffffff0U; c30d_servo_sweep_init();
    now=1983; assert(c30d_servo_sweep_step()==1500 && writes==0);
    now=1984; assert(c30d_servo_sweep_step()==1500);
    now=2004; assert(c30d_servo_sweep_step()==1501); /* start hold across tick wrap */
    printf("Stage %u sweep bounds, rate, enabled axes, startup, wrap: PASS\n", (unsigned)PT_STAGE);
    return 0;
}
