#include "pantilt_controller.h"
#include "pantilt_app.h"
#include "c30d_bsp.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static uint32_t now;
static unsigned enabled, writes;
static uint8_t relay;
static void (*rx)(uint8_t);
static void (*error_fn)(void);
volatile uint32_t c30d_uart_rx_errors;
void c30d_bsp_init(void) { now = 0; enabled = writes = 0; relay = 0U; }
void c30d_bsp_set_relay(uint8_t on) { relay = on; }
void c30d_bsp_enable_pwm(uint8_t axes, uint16_t y, uint16_t p) {
    (void)y; (void)p; enabled = axes;
}
void c30d_bsp_set_yaw_pulse_us(uint16_t us) { (void)us; ++writes; }
void c30d_bsp_set_pitch_pulse_us(uint16_t us) { (void)us; ++writes; }
uint32_t c30d_bsp_millis(void) { return now; }
uint32_t c30d_bsp_irq_save(void) { return 0; }
void c30d_bsp_irq_restore(uint32_t state) { (void)state; }
void c30d_bsp_uart_start_rx_it(void (*cb)(uint8_t), void (*err)(void)) { rx=cb; error_fn=err; }
void c30d_bsp_log(const char *s) { (void)s; }
static bool feed(pt_parser_t *p, const char *s, pt_target_t *t) {
    bool result = false;
    while (*s) if (pt_parser_push(p, (uint8_t)*s++, t)) result = true;
    return result;
}
static void send(const char *s) { while (*s) rx((uint8_t)*s++); }
static void close_to(float a, float b) { assert(fabsf(a-b) < 0.001f); }
static void center_at(uint32_t ms) {
    now = ms;
    send("$T,1,0,0\n");
    pantilt_app_step();
    assert(relay == pt_debug.relay_on);
}
static void hold_center(uint32_t start, uint32_t duration) {
    for (uint32_t elapsed = 0U; elapsed <= duration; elapsed += 20U)
        center_at(start + elapsed);
}
static void check_tracking_relay(void) {
    pantilt_app_init(true);
    now = 5000U;
    pantilt_app_step();
    assert(!relay && pt_debug.centered_ms == 0U);
    for (uint32_t ms = 5020U; ms < 7020U; ms += 20U) {
        now = ms;
        send("$T,1,50,-50\n");
        pantilt_app_step();
        assert(!relay);
    }
    center_at(7020U);
    assert(relay && pt_debug.centered_ms == 2000U);
    hold_center(7040U, 1000U);
    assert(relay && pt_debug.centered_ms == 2000U);

    now = 8060U; send("$T,1,51,0\n"); pantilt_app_step();
    assert(!relay && pt_debug.centered_ms == 0U);
    hold_center(8080U, 1000U); assert(!relay);
    now = 9100U; send("$T,1,-51,-1000\n"); pantilt_app_step();
    assert(!relay && pt_debug.centered_ms == 0U);
    hold_center(9120U, 1980U); assert(!relay);
    center_at(11120U); assert(relay);
    now = 11140U; send("$T,0,0,0\n"); pantilt_app_step();
    assert(!relay && pt_debug.centered_ms == 0U);
    hold_center(11160U, 1980U); assert(!relay);
    center_at(13160U); assert(relay);

    /* An off-center/lost frame cannot disappear into the latest-frame buffer. */
    now = 13180U; send("$T,1,51,0\n$T,1,0,0\n"); pantilt_app_step();
    assert(!relay && pt_debug.centered_ms == 0U);
    hold_center(13200U, 2000U); assert(relay);
    now = 15220U; send("$T,0,0,0\n$T,1,0,0\n"); pantilt_app_step();
    assert(!relay && pt_debug.centered_ms == 0U);

    pantilt_app_init(true); hold_center(0U, 2000U); assert(relay);
    now = 2299U; pantilt_app_step(); assert(relay);
    now = 2300U; pantilt_app_step();
    assert(!relay && pt_debug.centered_ms == 0U);
    hold_center(2320U, 1980U); assert(!relay);
    center_at(4320U); assert(relay);

    /* A fresh frame after a timeout must rearm even if no stale step ran. */
    pantilt_app_init(true); hold_center(0U, 2000U); assert(relay);
    center_at(2300U);
    assert(!relay && pt_debug.centered_ms == 0U);
    hold_center(2320U, 1980U); assert(relay);

    pantilt_app_init(true); now = 0U; send("$T,1,0,0\n");
    now = 300U; pantilt_app_step();
    assert(!relay && pt_debug.centered_ms == 0U);
    pantilt_app_init(false); hold_center(0U, 3000U);
    assert(!relay && !enabled && pt_debug.centered_ms == 0U);

    pantilt_app_init(true);
    hold_center(0xfffffc00U, 1980U); assert(!relay);
    center_at(0xfffffc00U + 2000U); assert(relay);
    pantilt_app_init(true);
    assert(!relay && pt_debug.centered_ms == 0U);
    /* Horizontal boundaries qualify even with extreme vertical error. */
    for (int x = -50; x <= 50; x += 100) {
        for (int y = -1000; y <= 1000; y += 2000) {
            char packet[32];
            pantilt_app_init(true);
            (void)snprintf(packet, sizeof(packet), "$T,1,%d,%d\n", x, y);
            for (now = 0U; now <= 2000U; now += 20U) {
                send(packet); pantilt_app_step();
                assert(relay == (now == 2000U));
            }
            assert(pt_debug.yaw_us != 1500U && pt_debug.pitch_us != 1500U);
            (void)snprintf(packet, sizeof(packet), "$T,1,%d,%d\n", x < 0 ? -51 : 51, y);
            send(packet); pantilt_app_step(); assert(!relay);
            hold_center(2040U, 2000U); assert(relay);
            for (unsigned i = 0U; i < 10U; ++i) {
                now += 20U;
                send("$T,1,0,-1000\n$T,1,0,1000\n");
                pantilt_app_step();
                assert(relay && pt_debug.centered_ms == 2000U);
            }
        }
    }
    puts("Tracking relay: center hold, boundaries, reset, loss, timeout, pending frames, wrap: PASS");
}
int main(void) {
    pt_parser_t p; pt_target_t t = {true,1000,1000};
    pt_parser_init(&p);
    assert(feed(&p,"$T,1,-1000,1000\r\n",&t) && t.ex==-1000 && t.ey==1000);
    const char *bad[] = {"$T,2,0,0\n","$T,1,1001,0\n","$T,1,9999999999999999999,0\n",
        "$T,1,,0\n","$T,1, 1,0\n","$T,1,+1,0\n","$T,1,1,0x\n","$T,1,0,0,0\n"};
    for (unsigned i=0;i<sizeof(bad)/sizeof(bad[0]);++i) assert(!feed(&p,bad[i],&t));
    assert(!feed(&p,"$T,1,0,0",&t));
    pt_parser_push(&p,0,&t);
    assert(!feed(&p,"junk\n",&t));
    for (unsigned i=0;i<100;++i) pt_parser_push(&p,'a',&t);
    assert(!feed(&p,"\n",&t));
    assert(feed(&p,"noise$T,1,5,6$T,0,0,0\n",&t) && !t.found);
    pt_parser_discard(&p);
    assert(!feed(&p,"T,1,0,0\n",&t));
    assert(feed(&p,"$T,1,0,0\n",&t));

    pt_controller_t c; pt_controller_init(&c,0);
    assert(c.yaw_us==1500 && c.pitch_us==1500);
    t=(pt_target_t){true,15,-15};
    pt_controller_update(&c,&t,20,20);
    close_to(c.yaw_deg,135); close_to(c.pitch_deg,90);
    t=(pt_target_t){true,1000,1000};
    pt_controller_update(&c,&t,40,40);
    close_to(c.yaw_deg,133.8f); close_to(c.pitch_deg,89.58f);
    pt_controller_update(&c,NULL,0,60); /* retained error, not a single-frame step */
    close_to(c.yaw_deg,132.6f);
    float old=c.yaw_deg;
    pt_controller_update(&c,NULL,0,339);
    assert(fabsf(c.yaw_deg-old) <= PT_YAW_MAX_DPS*.02f+.001f);
    old=c.yaw_deg;
    pt_controller_update(&c,NULL,0,340);
    close_to(c.yaw_deg,old); assert(!c.have_command);
    t.found=false; pt_controller_update(&c,&t,360,360);
    close_to(c.yaw_deg,old);
    t.found=true; pt_controller_update(&c,&t,100,500);
    close_to(c.yaw_deg,old); /* stale pending frame cannot resume motion */
    for (uint32_t ms=520;ms<10520;ms+=20) pt_controller_update(&c,&t,ms,ms);
    close_to(c.yaw_deg,PT_YAW_MIN_DEG); close_to(c.pitch_deg,PT_PITCH_MIN_DEG);
    assert(c.yaw_us==944 && c.pitch_us==1167); /* travel independent of limits */
    t.ex=-1000; t.ey=-1000;
    for (uint32_t ms=10520;ms<20520;ms+=20) pt_controller_update(&c,&t,ms,ms);
    close_to(c.yaw_deg,PT_YAW_MAX_DEG); close_to(c.pitch_deg,PT_PITCH_MAX_DEG);
    assert(c.yaw_us==2056 && c.pitch_us==1833);
    pt_controller_init(&c,0xfffffff0U);
    t.ex=1000; pt_controller_update(&c,&t,0xfffffff0U,4U);
    close_to(c.yaw_deg,133.8f); assert(c.have_command);
    old=c.yaw_deg; pt_controller_update(&c,NULL,0,284U);
    close_to(c.yaw_deg,old); assert(!c.have_command); /* 300ms across wrap */

    /* Errors inside the former deadband must now produce a correction. */
    pt_controller_init(&c,0);
    t=(pt_target_t){true,30,-30};
    pt_controller_update(&c,&t,20,20);
    assert(c.yaw_deg<135.0f && c.pitch_deg>90.0f);
    t.ex=-30; t.ey=30;
    old=c.yaw_deg;
    float old_pitch=c.pitch_deg;
    pt_controller_update(&c,&t,40,40);
    assert(c.yaw_deg>old && c.pitch_deg<old_pitch);

    pantilt_app_init(false);
    assert(pt_debug.rx_bytes==0 && pt_debug.valid_frames==0);
    send("$T,0,0,0");
    assert(pt_debug.rx_bytes==8 && pt_debug.valid_frames==0 && pt_debug.bad_lines==0);
    send("\n");
    assert(pt_debug.rx_bytes==9 && pt_debug.valid_frames==1);
    send("noise\n");
    assert(pt_debug.rx_bytes==15 && pt_debug.valid_frames==1 && pt_debug.bad_lines==1);
    now=20; pantilt_app_step(); assert(enabled==0 && writes==0);
    pantilt_app_init(false); assert(pt_debug.rx_bytes==0);
    send("$T,1,1000,0\n");
    now=20; pantilt_app_step(); assert(enabled==0 && writes==0 && pt_debug.valid_frames==1);
    pantilt_app_init(true); assert(enabled==(C30D_PWM_YAW|C30D_PWM_PITCH));
    send("$T,1,1000,0\n$T,0,0,0\n");
    now=20; pantilt_app_step(); assert(!pt_debug.tracking && pt_debug.yaw_us==1500);
    send("$T,1,1000,0\n"); now=40; pantilt_app_step();
    assert(pt_debug.tracking && pt_debug.yaw_us<1500);
    uint16_t last=pt_debug.yaw_us;
    now=400; pantilt_app_step(); assert(!pt_debug.tracking && pt_debug.yaw_us==last);
    send("$T,1,1000,"); error_fn(); send("0\n");
    assert(pt_debug.valid_frames==3);
    send("$T,0,0,0\n"); assert(pt_debug.valid_frames==4);
    puts("C parser/controller/app checks: PASS");
    check_tracking_relay();
    return 0;
}
