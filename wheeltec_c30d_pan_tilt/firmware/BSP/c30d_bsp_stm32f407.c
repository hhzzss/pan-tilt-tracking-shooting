/* Green C30D with four motor ports, STM32F407VET6.
 * PC6/PC7: TIM3 CH1/CH2 AF2; PA3: USART2 RX AF7 (receive only).
 * PC12: active-low relay IN, open drain, released at startup.
 * HSI 16 MHz avoids guessing the external oscillator frequency. */
#include "c30d_bsp.h"
#include "pantilt_config.h"
#include "stm32f4xx.h"
static volatile uint32_t ticks;
volatile uint32_t c30d_uart_rx_errors;
static void (*rx_callback)(uint8_t);
static void (*error_callback)(void);
static void alternate(GPIO_TypeDef *port, unsigned pin, unsigned af) {
    port->AFR[pin / 8U] = (port->AFR[pin / 8U] & ~(15UL << ((pin % 8U) * 4U))) |
        ((uint32_t)af << ((pin % 8U) * 4U));
    port->OTYPER &= ~(1UL << pin);
    port->OSPEEDR = (port->OSPEEDR & ~(3UL << (pin * 2U))) | (1UL << (pin * 2U));
    port->MODER = (port->MODER & ~(3UL << (pin * 2U))) | (2UL << (pin * 2U));
}
void c30d_bsp_init(void) {
    RCC->CR |= RCC_CR_HSION;
    while (!(RCC->CR & RCC_CR_HSIRDY)) {}
    RCC->CFGR &= ~RCC_CFGR_SW;
    while (RCC->CFGR & RCC_CFGR_SWS) {}
    RCC->CFGR = 0U;
    RCC->CR &= ~RCC_CR_PLLON;
    SystemCoreClock = 16000000U;
    SCB->VTOR = FLASH_BASE;
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOCEN | RCC_AHB1ENR_GPIOAEN;
    RCC->APB1ENR |= RCC_APB1ENR_TIM3EN | RCC_APB1ENR_USART2EN;
    RCC->APB2ENR |= RCC_APB2ENR_USART1EN;
    (void)RCC->AHB1ENR;
    /* Preload OFF before output mode; the relay module supplies the pull-up. */
    GPIOC->BSRR = 1UL << 12;
    GPIOC->OTYPER |= 1UL << 12;
    GPIOC->PUPDR &= ~(3UL << 24);
    GPIOC->OSPEEDR &= ~(3UL << 24);
    GPIOC->MODER = (GPIOC->MODER & ~(3UL << 24)) | (1UL << 24);
    /* Both signals stay low until a stage explicitly enables its channels. */
    GPIOC->BSRR = (1UL << 22) | (1UL << 23);
    GPIOC->MODER = (GPIOC->MODER & ~((3UL << 12) | (3UL << 14))) |
        (1UL << 12) | (1UL << 14);
    GPIOC->PUPDR &= ~((3UL << 12) | (3UL << 14));
    TIM3->CR1 = 0U;
    TIM3->CCER = 0U;
    TIM3->PSC = 15U;
    TIM3->ARR = PT_SERVO_PERIOD_US - 1U;
    TIM3->CCR1 = 1500U;
    TIM3->CCR2 = 1500U;
    TIM3->CCMR1 = TIM_CCMR1_OC1PE | TIM_CCMR1_OC2PE | (6UL << 4) | (6UL << 12);
    TIM3->EGR = TIM_EGR_UG;
    TIM3->CR1 = TIM_CR1_ARPE;
    /* UART1 connects to the CH9102 USB bridge for diagnostics. */
    alternate(GPIOA, 9U, 7U);
    USART1->CR1 = 0U;
    USART1->BRR = (16000000U + PT_UART_BAUD / 2U) / PT_UART_BAUD;
    USART1->CR2 = 0U;
    USART1->CR3 = 0U;
    USART1->CR1 = USART_CR1_UE | USART_CR1_TE;
    ticks = 0U;
    (void)SysTick_Config(SystemCoreClock / 1000U);
}
void c30d_bsp_enable_pwm(uint8_t axes, uint16_t yaw_us, uint16_t pitch_us) {
    c30d_bsp_set_yaw_pulse_us(yaw_us);
    c30d_bsp_set_pitch_pulse_us(pitch_us);
    TIM3->EGR = TIM_EGR_UG;
    if (axes & C30D_PWM_YAW) alternate(GPIOC, 6U, 2U);
    if (axes & C30D_PWM_PITCH) alternate(GPIOC, 7U, 2U);
    TIM3->CCER = ((axes & C30D_PWM_YAW) ? TIM_CCER_CC1E : 0U) |
        ((axes & C30D_PWM_PITCH) ? TIM_CCER_CC2E : 0U);
    TIM3->CR1 |= TIM_CR1_CEN;
}
static uint16_t safe_pulse(uint16_t us) {
    if (us < PT_SERVO_MIN_US) return PT_SERVO_MIN_US;
    return us > PT_SERVO_MAX_US ? PT_SERVO_MAX_US : us;
}
void c30d_bsp_set_yaw_pulse_us(uint16_t us) { TIM3->CCR1 = safe_pulse(us); }
void c30d_bsp_set_pitch_pulse_us(uint16_t us) { TIM3->CCR2 = safe_pulse(us); }
void c30d_bsp_set_relay(uint8_t enabled) {
    GPIOC->BSRR = enabled ? (1UL << 28) : (1UL << 12);
}
uint32_t c30d_bsp_millis(void) { return ticks; }
void SysTick_Handler(void) { ++ticks; }
uint32_t c30d_bsp_irq_save(void) {
    uint32_t state = __get_PRIMASK();
    __disable_irq();
    return state;
}
void c30d_bsp_irq_restore(uint32_t state) { __set_PRIMASK(state); }
void c30d_bsp_uart_start_rx_it(void (*on_byte)(uint8_t), void (*on_error)(void)) {
    rx_callback = on_byte;
    error_callback = on_error;
    /* PA3 is exposed on the user's reserved IO header; PA2 stays unused. */
    alternate(GPIOA, 3U, 7U);
    GPIOA->PUPDR = (GPIOA->PUPDR & ~(3UL << 6)) | (1UL << 6);
    USART2->CR1 = 0U;
    USART2->BRR = (16000000U + PT_UART_BAUD / 2U) / PT_UART_BAUD;
    USART2->CR2 = 0U;
    USART2->CR3 = USART_CR3_EIE;
    (void)USART2->SR;
    (void)USART2->DR;
    NVIC_SetPriority(USART2_IRQn, 2U);
    NVIC_ClearPendingIRQ(USART2_IRQn);
    NVIC_EnableIRQ(USART2_IRQn);
    USART2->CR1 = USART_CR1_UE | USART_CR1_RE |
        USART_CR1_RXNEIE | USART_CR1_PEIE;
}
void USART2_IRQHandler(void) {
    uint32_t status = USART2->SR;
    if (status & (USART_SR_ORE | USART_SR_NE | USART_SR_FE | USART_SR_PE)) {
        (void)USART2->DR; /* SR then DR clears errors; RX stays enabled. */
        ++c30d_uart_rx_errors;
        if (error_callback) error_callback();
    } else if (status & USART_SR_RXNE) {
        uint8_t byte = (uint8_t)USART2->DR;
        if (rx_callback) rx_callback(byte);
    }
}
void c30d_bsp_log(const char *text) {
    while (*text) {
        uint32_t start = ticks;
        while (!(USART1->SR & USART_SR_TXE)) {
            if ((uint32_t)(ticks - start) > 10U) return;
        }
        USART1->DR = (uint8_t)*text++;
    }
}
