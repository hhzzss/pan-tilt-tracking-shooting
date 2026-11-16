#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "pantilt_protocol.h"
typedef struct {
    float yaw_deg, pitch_deg;
    uint16_t yaw_us, pitch_us;
    uint32_t last_command_ms, last_update_ms;
    bool have_command, target_found;
    int16_t ex, ey;
} pt_controller_t;
void pt_controller_init(pt_controller_t *c, uint32_t now_ms);
void pt_controller_update(pt_controller_t *c, const pt_target_t *target,
                          uint32_t received_ms, uint32_t now_ms);
