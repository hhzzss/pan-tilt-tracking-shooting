#include "pantilt_app.h"
#include "pantilt_controller.h"
#include "pantilt_protocol.h"
#include "c30d_bsp.h"
#include <stddef.h>
#include <string.h>
static pt_parser_t parser;
static pt_controller_t controller;
static volatile pt_target_t pending;
static volatile uint32_t pending_ms;
static volatile bool pending_valid;
static volatile bool pending_center_break;
static bool outputs_enabled;
static bool center_timing;
static uint32_t center_started_ms;
volatile pt_debug_t pt_debug;
static bool target_centered(int16_t ex) {
    return ex >= -PT_RELAY_CENTER_TOLERANCE && ex <= PT_RELAY_CENTER_TOLERANCE;
}
/* Latest complete frame wins; a backlog must not become a queue of moves. */
void pantilt_on_uart_byte(uint8_t byte) {
    ++pt_debug.rx_bytes;
    pt_target_t decoded;
    if (pt_parser_push(&parser, byte, &decoded)) {
        uint32_t received = c30d_bsp_millis();
        /* Keep breaks even when a later centered frame replaces pending. */
        if (!decoded.found || !target_centered(decoded.ex) ||
            (pt_debug.valid_frames != 0U &&
             (uint32_t)(received - pending_ms) >= PT_COMMAND_TIMEOUT_MS))
            pending_center_break = true;
        pending = decoded;
        pending_ms = received;
        pending_valid = true;
        ++pt_debug.valid_frames;
    }
    pt_debug.bad_lines = parser.rejected_lines;
}
static void uart_error(void) { pt_parser_discard(&parser); }
void pantilt_app_init(bool enable_pwm) {
    c30d_bsp_init();
    pt_parser_init(&parser);
    memset((void *)&pt_debug, 0, sizeof(pt_debug));
    pending_valid = false;
    pending_center_break = false;
    pending_ms = 0U;
    center_timing = false;
    center_started_ms = 0U;
    c30d_bsp_set_relay(0U);
    outputs_enabled = enable_pwm;
    pt_controller_init(&controller, c30d_bsp_millis());
    pt_debug.yaw_us = controller.yaw_us;
    pt_debug.pitch_us = controller.pitch_us;
    if (enable_pwm) c30d_bsp_enable_pwm(C30D_PWM_YAW | C30D_PWM_PITCH,
                                       controller.yaw_us, controller.pitch_us);
    c30d_bsp_uart_start_rx_it(pantilt_on_uart_byte, uart_error);
}
void pantilt_app_step(void) {
    pt_target_t command = {false, 0, 0};
    bool have_command = false;
    uint32_t received = 0U;
    uint32_t state = c30d_bsp_irq_save();
    bool center_break = pending_center_break;
    pending_center_break = false;
    if (pending_valid) {
        command = pending;
        received = pending_ms;
        pending_valid = false;
        have_command = true;
    }
    c30d_bsp_irq_restore(state);
    uint32_t now = c30d_bsp_millis();
    if (have_command) {
        pt_debug.last_rx_ms = received;
        pt_debug.found = command.found ? 1U : 0U;
        pt_debug.ex = command.ex;
        pt_debug.ey = command.ey;
    }
    if (outputs_enabled) {
        pt_controller_update(&controller, have_command ? &command : NULL, received, now);
        c30d_bsp_set_yaw_pulse_us(controller.yaw_us);
        c30d_bsp_set_pitch_pulse_us(controller.pitch_us);
        pt_debug.yaw_us = controller.yaw_us;
        pt_debug.pitch_us = controller.pitch_us;
        pt_debug.tracking = controller.have_command && controller.target_found;
        bool centered = pt_debug.tracking && target_centered(controller.ex);
        if (center_break || !centered) {
            center_timing = false;
            pt_debug.centered_ms = 0U;
        }
        if (centered) {
            if (!center_timing) {
                center_started_ms = now;
                center_timing = true;
            }
            if (pt_debug.centered_ms < PT_RELAY_CENTER_HOLD_MS) {
                uint32_t held = now - center_started_ms;
                pt_debug.centered_ms = held < PT_RELAY_CENTER_HOLD_MS ?
                    held : PT_RELAY_CENTER_HOLD_MS;
            }
        }
        uint8_t relay_on = centered && pt_debug.centered_ms >= PT_RELAY_CENTER_HOLD_MS;
        if (relay_on != pt_debug.relay_on) {
            c30d_bsp_set_relay(relay_on);
            pt_debug.relay_on = relay_on;
        }
    }
}
