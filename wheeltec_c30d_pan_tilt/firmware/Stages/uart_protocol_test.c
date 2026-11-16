#include "uart_protocol_test.h"
#include "pantilt_app.h"
/* Actual UART2 reception. PWM stays disabled throughout stage 3. */
int c30d_uart_protocol_test_run(void) {
    pantilt_app_init(false);
    return 0;
}
