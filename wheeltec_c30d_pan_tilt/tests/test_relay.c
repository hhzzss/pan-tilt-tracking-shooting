/* Run the actual stage-7 main loop across the millisecond counter wrap. */
#define main relay_firmware_main
#include "../firmware/Core/Src/main.c"
#undef main
#include <assert.h>
#include <stdlib.h>

static uint32_t elapsed;
static unsigned writes;
static unsigned initialized;

void c30d_bsp_init(void) {
    ++initialized;
}
uint32_t c30d_bsp_millis(void) {
    return 0xffffff00U + elapsed++;
}
void c30d_bsp_log(const char *text) {
    (void)text;
}
void c30d_bsp_set_relay(uint8_t enabled) {
    static const uint32_t expected_ms[] = {2000U, 3000U, 5000U, 6000U};
    assert(initialized == 1U);
    assert(writes < 4U);
    assert(elapsed - 1U == expected_ms[writes]);
    assert(enabled == ((writes % 2U) == 0U));
    if (++writes == 4U) {
        puts("Relay startup OFF, OFF 2s / ON 1s, tick wrap, no PWM: PASS");
        exit(0);
    }
}
int main(void) {
    return relay_firmware_main();
}
