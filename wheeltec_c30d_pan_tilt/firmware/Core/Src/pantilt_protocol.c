#include "pantilt_protocol.h"
#include <string.h>
/* Bounded conversion rejects empty fields, spaces and overflow. */
static bool error_field(const char **cursor, char delimiter, int16_t *value) {
    const char *s = *cursor;
    int sign = 1, number = 0;
    if (*s == '-') { sign = -1; ++s; }
    if (*s < '0' || *s > '9') return false;
    unsigned digits = 0U;
    while (*s >= '0' && *s <= '9') {
        if (++digits > 4U) return false;
        number = number * 10 + (*s++ - '0');
        if (number > 1000) return false;
    }
    if (*s != delimiter) return false;
    *value = (int16_t)(sign * number);
    *cursor = s + (delimiter != '\0' ? 1 : 0);
    return true;
}
void pt_parser_init(pt_parser_t *p) { memset(p, 0, sizeof(*p)); }
void pt_parser_discard(pt_parser_t *p) { p->length = 0U; p->overflow = true; }
bool pt_parser_push(pt_parser_t *p, uint8_t byte, pt_target_t *out) {
    if (byte == '$') { p->length = 0U; p->overflow = false; }
    if (byte != '\n') {
        if (byte == 0U || p->length >= PT_PROTOCOL_MAX_LINE) p->overflow = true;
        else if (!p->overflow) p->line[p->length++] = (char)byte;
        return false;
    }
    if (p->length && p->line[p->length - 1U] == '\r') --p->length;
    p->line[p->length] = '\0';
    bool ok = false;
    pt_target_t decoded;
    if (!p->overflow && p->length >= 8U &&
        p->line[0] == '$' && p->line[1] == 'T' && p->line[2] == ',' &&
        (p->line[3] == '0' || p->line[3] == '1') && p->line[4] == ',') {
        const char *cursor = p->line + 5;
        decoded.found = p->line[3] == '1';
        if (error_field(&cursor, ',', &decoded.ex) && error_field(&cursor, '\0', &decoded.ey)) {
            *out = decoded;
            ok = true;
        }
    }
    if (!ok) ++p->rejected_lines;
    p->length = 0U;
    p->overflow = false;
    return ok;
}
