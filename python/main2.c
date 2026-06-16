/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Distributeur d'aliments — STM32 Nucleo L412KB
  ******************************************************************************
  * Matériel :
  *   HC-SR04  : TRIG → PA0 (GPIO Out)   ECHO → PA1 (GPIO In, polling)
  *   ULN2003  : IN4→PA5  IN1→PA6  IN2→PA7  IN3→PA9
  *   28BYJ-48 : piloté via Stepper_Step()
  *   UART2    : PA2/PA3 — Virtual COM (printf redirigé)
  * Horloge   : MSI 4 MHz, TIM2 prescaler=3 → 1 µs/tick
  ******************************************************************************
  */
/* USER CODE END Header */

#include "main.h"
#include "hcsr04.h"
#include "stepper.h"
#include <stdio.h>

extern UART_HandleTypeDef huart2;

/* ---- Paramètres mécaniques — à calibrer selon ton distributeur ---- */
#define DISTANCE_PLEIN_MM         390   /* Distance (mm) casier VIDE               */
#define EPAISSEUR_ALIMENT_MM  60   /* Épaisseur d'un aliment (mm)             */
#define SEUIL_ALERTE           3   /* Stock restant → LED alerte              */
#define HYSTERESIS_MM          8   /* Anti-rebond mesure (évite faux déclench)*/
#define PAS_PAR_ALIMENT       5096   /* Pas moteur pour avancer d'1 emplacement */
#define DELAI_PAS_US        800   /* Délai inter-pas µs (vitesse moteur)     */
#define STOCK_MAX  (DISTANCE_PLEIN_MM / EPAISSEUR_ALIMENT_MM)
/* ---- Handles HAL ---- */
TIM_HandleTypeDef htim2;
UART_HandleTypeDef huart2;

/* ---- Prototypes fonctions MX (générées CubeIDE) ---- */
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_TIM2_Init(void);
static void MX_USART2_UART_Init(void);

/* ---- Retarget printf → UART2 ---- */
int _write(int file, char *ptr, int len)
{
    HAL_UART_Transmit(&huart2, (uint8_t*)ptr, len, HAL_MAX_DELAY);
    return len;
}

/* =========================================================== */
int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_TIM2_Init();
    MX_USART2_UART_Init();

    /* Démarrage du compteur TIM2 (base µs pour HC-SR04) */
    HAL_TIM_Base_Start(&htim2);

    printf("=== Distributeur aliments - BOOT ===\r\n");
    printf("PleinRef=%d mm | Epaisseur=%d mm | StockMax=%d | Alerte=%d aliments\r\n",
           DISTANCE_PLEIN_MM, EPAISSEUR_ALIMENT_MM, STOCK_MAX, SEUIL_ALERTE);



    while (1)
    {
        /* --- 1. Mesure HC-SR04 (retourne des cm) → on convertit en mm --- */
        float dist_cm = HCSR04_Read();
        uint32_t dist_mm = (uint32_t)(dist_cm * 10.0f);

        /* Filtre : ignore mesures aberrantes */
        if (dist_mm == 0 || dist_mm > 500)
        {
            printf("Mesure invalide (%lu mm), ignoree\r\n", dist_mm);
            HAL_Delay(500);
            continue;
        }

        /* --- 2. Calcul stock restant --- */
        /* --- 2. Calcul stock restant --- */
        uint32_t manquants = dist_mm / EPAISSEUR_ALIMENT_MM;
        int32_t stock = (int32_t)STOCK_MAX - (int32_t)manquants;
        if (stock < 0) stock = 0;

        printf("Distance: %lu mm | Stock: %ld aliments\r\n", dist_mm, stock);



        /* --- 4. Alerte stock faible → LED PC3 --- */
        if (stock <= SEUIL_ALERTE)
        {
            HAL_GPIO_WritePin(GPIOC, GPIO_PIN_3, GPIO_PIN_SET);
            printf("/!\\ Stock bas : %ld aliments\r\n", stock);
        }
        else
        {
            HAL_GPIO_WritePin(GPIOC, GPIO_PIN_3, GPIO_PIN_RESET);
        }

        /* --- 5. Casier vide --- */
        if (stock == 0)
            printf("!!! CASIER VIDE - Remplissage requis !!!\r\n");



        HAL_Delay(1000);
    }
}

/* =========================================================== */
/* FONCTIONS GÉNÉRÉES PAR CUBEMX — NE PAS MODIFIER             */
/* =========================================================== */

void SystemClock_Config(void)
{
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

    if (HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1) != HAL_OK)
        Error_Handler();

    RCC_OscInitStruct.OscillatorType      = RCC_OSCILLATORTYPE_MSI;
    RCC_OscInitStruct.MSIState            = RCC_MSI_ON;
    RCC_OscInitStruct.MSICalibrationValue = 0;
    RCC_OscInitStruct.MSIClockRange       = RCC_MSIRANGE_6;   /* 4 MHz */
    RCC_OscInitStruct.PLL.PLLState        = RCC_PLL_NONE;
    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
        Error_Handler();

    RCC_ClkInitStruct.ClockType      = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK
                                     | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource   = RCC_SYSCLKSOURCE_MSI;
    RCC_ClkInitStruct.AHBCLKDivider  = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
    if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
        Error_Handler();
}

static void MX_TIM2_Init(void)
{
    TIM_ClockConfigTypeDef sClockSourceConfig = {0};
    TIM_MasterConfigTypeDef sMasterConfig     = {0};

    htim2.Instance               = TIM2;
    htim2.Init.Prescaler         = 3;            /* 4 MHz / 4 = 1 MHz → 1 µs/tick */
    htim2.Init.CounterMode       = TIM_COUNTERMODE_UP;
    htim2.Init.Period            = 4294967295;
    htim2.Init.ClockDivision     = TIM_CLOCKDIVISION_DIV1;
    htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
    if (HAL_TIM_Base_Init(&htim2) != HAL_OK)
        Error_Handler();

    sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
    if (HAL_TIM_ConfigClockSource(&htim2, &sClockSourceConfig) != HAL_OK)
        Error_Handler();

    sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
    sMasterConfig.MasterSlaveMode     = TIM_MASTERSLAVEMODE_DISABLE;
    if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
        Error_Handler();
}

static void MX_USART2_UART_Init(void)
{
    huart2.Instance                    = USART2;
    huart2.Init.BaudRate               = 115200;
    huart2.Init.WordLength             = UART_WORDLENGTH_8B;
    huart2.Init.StopBits               = UART_STOPBITS_1;
    huart2.Init.Parity                 = UART_PARITY_NONE;
    huart2.Init.Mode                   = UART_MODE_TX_RX;
    huart2.Init.HwFlowCtl              = UART_HWCONTROL_NONE;
    huart2.Init.OverSampling           = UART_OVERSAMPLING_16;
    huart2.Init.OneBitSampling         = UART_ONE_BIT_SAMPLE_DISABLE;
    huart2.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_NO_INIT;
    if (HAL_UART_Init(&huart2) != HAL_OK)
        Error_Handler();
}

static void MX_GPIO_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();   /* AJOUT : horloge GPIOC pour LED PC3 */

    /* PA0 - TRIG HC-SR04 (sortie) */
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_0, GPIO_PIN_RESET);
    GPIO_InitStruct.Pin   = GPIO_PIN_0;
    GPIO_InitStruct.Mode  = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull  = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    /* PA1 - ECHO HC-SR04 (entrée) */
    GPIO_InitStruct.Pin  = GPIO_PIN_1;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    /* PA5, PA6, PA7, PA9 - ULN2003 IN4, IN1, IN2, IN3 (sorties moteur) */
    GPIO_InitStruct.Pin   = GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7 | GPIO_PIN_9;
    GPIO_InitStruct.Mode  = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull  = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7 | GPIO_PIN_9,
                      GPIO_PIN_RESET);

    /* PC3 - LED alerte stock faible (AJOUT) */
    GPIO_InitStruct.Pin   = GPIO_PIN_3;
    GPIO_InitStruct.Mode  = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull  = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_3, GPIO_PIN_RESET);
}

void Error_Handler(void)
{
    __disable_irq();
    while (1) {}
}

#ifdef USE_FULL_ASSERT
void assert_failed(uint8_t *file, uint32_t line)
{
    /* printf("Assert failed: file %s line %d\r\n", file, line); */
}
#endif
