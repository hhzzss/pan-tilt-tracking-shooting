#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "pantilt_config.h"
typedef struct { bool found; int16_t ex, ey; } pt_target_t;
typedef struct {
    char line[PT_PROTOCOL_MAX_LINE + 1U];
    uint8_t length;
    bool overflow;
    uint32_t rejected_lines;
} pt_parser_t;
void pt_parser_init(pt_parser_t *p);
void pt_parser_discard(pt_parser_t *p);
bool pt_parser_push(pt_parser_t *p, uint8_t byte, pt_target_t *out);
