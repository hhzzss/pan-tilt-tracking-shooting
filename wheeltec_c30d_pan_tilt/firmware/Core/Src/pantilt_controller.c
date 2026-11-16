#include "pantilt_controller.h"
#include <string.h>
static float clamp_f(float x, float low, float high) {
    return x < low ? low : (x > high ? high : x);
}
static uint16_t angle_to_us(float angle, float travel) {
    float us = (float)PT_SERVO_MIN_US +
        angle / travel * (float)(PT_SERVO_MAX_US - PT_SERVO_MIN_US);
    return (uint16_t)(clamp_f(us, PT_SERVO_MIN_US, PT_SERVO_MAX_US) + 0.5f);
}
static float velocity(int16_t error, int deadband, float kp, float limit) {
    int magnitude = error < 0 ? -(int)error : (int)error;
    if (magnitude <= deadband) return 0.0f;
    float speed = kp * (float)(magnitude - deadband) / (float)(1000 - deadband);
    speed = clamp_f(speed, 0.0f, limit);
    return error < 0 ? -speed : speed;
}
void pt_controller_init(pt_controller_t *c, uint32_t now_ms) {
    memset(c, 0, sizeof(*c));
    c->yaw_deg = clamp_f(PT_YAW_HOME_DEG, PT_YAW_MIN_DEG, PT_YAW_MAX_DEG);
    c->pitch_deg = clamp_f(PT_PITCH_HOME_DEG, PT_PITCH_MIN_DEG, PT_PITCH_MAX_DEG);
    c->yaw_us = angle_to_us(c->yaw_deg, PT_YAW_TRAVEL_DEG);
    c->pitch_us = angle_to_us(c->pitch_deg, PT_PITCH_TRAVEL_DEG);
    c->last_update_ms = now_ms;
}
void pt_controller_update(pt_controller_t *c, const pt_target_t *target,
                          uint32_t received_ms, uint32_t now_ms) {
    uint32_t elapsed_ms = now_ms - c->last_update_ms;
    c->last_update_ms = now_ms;
    /* Do not catch up a stalled loop with a large mechanical jump. */
    if (elapsed_ms > PT_CONTROL_PERIOD_MS) elapsed_ms = PT_CONTROL_PERIOD_MS;
    if (target) {
        c->last_command_ms = received_ms;
        c->have_command = (uint32_t)(now_ms - received_ms) < PT_COMMAND_TIMEOUT_MS;
        c->target_found = target->found;
        c->ex = target->ex;
        c->ey = target->ey;
    }
    if ((uint32_t)(now_ms - c->last_command_ms) >= PT_COMMAND_TIMEOUT_MS)
        c->have_command = false;
    if (c->have_command && c->target_found) {
        float dt = (float)elapsed_ms / 1000.0f;
        c->yaw_deg = clamp_f(c->yaw_deg + dt * PT_YAW_SIGN *
            velocity(c->ex, PT_YAW_DEADBAND, PT_YAW_KP_DPS, PT_YAW_MAX_DPS),
            PT_YAW_MIN_DEG, PT_YAW_MAX_DEG);
        c->pitch_deg = clamp_f(c->pitch_deg + dt * PT_PITCH_SIGN *
            velocity(c->ey, PT_PITCH_DEADBAND, PT_PITCH_KP_DPS, PT_PITCH_MAX_DPS),
            PT_PITCH_MIN_DEG, PT_PITCH_MAX_DEG);
    }
    /* Lost target or stale UART: retain PWM at the last commanded angle. */
    c->yaw_us = angle_to_us(c->yaw_deg, PT_YAW_TRAVEL_DEG);
    c->pitch_us = angle_to_us(c->pitch_deg, PT_PITCH_TRAVEL_DEG);
}
