#pragma once
#include <stdint.h>
#define C30D_PWM_YAW   1U
#define C30D_PWM_PITCH 2U
void c30d_bsp_init(void);
void c30d_bsp_enable_pwm(uint8_t axes, uint16_t yaw_us, uint16_t pitch_us);
void c30d_bsp_set_yaw_pulse_us(uint16_t pulse_us);
void c30d_bsp_set_pitch_pulse_us(uint16_t pulse_us);
/* 1: sink PC12 to energize a LOW-trigger relay; 0: release PC12 (OFF). */
void c30d_bsp_set_relay(uint8_t enabled);
uint32_t c30d_bsp_millis(void);
uint32_t c30d_bsp_irq_save(void);
void c30d_bsp_irq_restore(uint32_t state);
void c30d_bsp_uart_start_rx_it(void (*on_byte)(uint8_t), void (*on_error)(void));
void c30d_bsp_log(const char *text);
extern volatile uint32_t c30d_uart_rx_errors;
