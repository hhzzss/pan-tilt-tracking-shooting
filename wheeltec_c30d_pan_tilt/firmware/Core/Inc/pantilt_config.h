#pragma once
/* 1: yaw; 2: pitch; 3: UART; 4: tracking; 5: dual sweep; 6: pitch; 7: relay. */
#ifndef PT_STAGE
#define PT_STAGE 5
#endif
#define PT_UART_BAUD                   115200U
#define PT_CONTROL_PERIOD_MS           20U
#define PT_COMMAND_TIMEOUT_MS          300U
#define PT_PROTOCOL_MAX_LINE           64U
/* S20F position variants, official item 645346572889. */
#define PT_SERVO_MIN_US                500U
#define PT_SERVO_MAX_US                2500U
#define PT_SERVO_PERIOD_US             20000U
#define PT_YAW_TRAVEL_DEG              270.0f
#define PT_PITCH_TRAVEL_DEG            180.0f
#define PT_YAW_HOME_DEG                135.0f
#define PT_PITCH_HOME_DEG              90.0f
/* Mechanical window: verify with your assembled mechanism.
 * These limits do not change the physical angle-to-pulse calibration. */
#define PT_YAW_MIN_DEG                 60.0f
#define PT_YAW_MAX_DEG                 210.0f
#define PT_PITCH_MIN_DEG               60.0f
#define PT_PITCH_MAX_DEG               120.0f
#define PT_YAW_DEADBAND                15
#define PT_PITCH_DEADBAND              15
/* Lamp acceptance is wider than the servo correction deadband. */
#define PT_RELAY_CENTER_TOLERANCE      50
#define PT_RELAY_CENTER_HOLD_MS        2000U
/* Proportional angular velocity: degrees/second at full normalized error. */
#define PT_YAW_KP_DPS                  60.0f
#define PT_PITCH_KP_DPS                21.0f
#define PT_YAW_MAX_DPS                 60.0f
#define PT_PITCH_MAX_DPS               25.0f
#define PT_YAW_SIGN                    (-1.0f)
#define PT_PITCH_SIGN                  (-1.0f)
#ifndef PT_TEST_PULSE_US
#define PT_TEST_PULSE_US               1500U
#endif
#if PT_TEST_PULSE_US < 1400U || PT_TEST_PULSE_US > 1600U
#error "First test must stay within 1400..1600 us"
#endif
#if PT_STAGE == 5
#define PT_SWEEP_MIN_US                1400U
#define PT_SWEEP_MAX_US                1600U
#else
#define PT_SWEEP_MIN_US                1450U
#define PT_SWEEP_MAX_US                1550U
#endif
#define PT_SWEEP_STEP_US               1U
#define PT_SWEEP_START_HOLD_MS         2000U
#if PT_SWEEP_MIN_US < 1400U || PT_SWEEP_MAX_US > 1600U || \
    PT_SWEEP_MIN_US >= 1500U || PT_SWEEP_MAX_US <= 1500U || \
    PT_SWEEP_STEP_US == 0U || PT_SWEEP_STEP_US > 5U
#error "Keep initial sweep small and slow around 1500 us"
#endif
#if PT_STAGE < 1 || PT_STAGE > 7
#error "PT_STAGE must be 1, 2, 3, 4, 5, 6 or 7"
#endif
