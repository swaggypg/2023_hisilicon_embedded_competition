#include <stdio.h>

#include <unistd.h>
#include <hi_types_base.h>
#include <hi_io.h>
#include <hi_early_debug.h>
#include <hi_gpio.h>
#include <hi_task.h>
#include "ohos_init.h"
#include "cmsis_os2.h"

#include <unistd.h>
#include <hi_types_base.h>

#define APP_DEMO_ADC

#include <hi_adc.h>
#include <hi_stdlib.h>
#include <hi_early_debug.h>


#define KEY_EVENT_NONE      0
#define KEY_EVENT_S1      1
#define KEY_EVENT_S2      2
#define KEY_EVENT_S3      3
#define KEY_EVENT_S4      4

#define ADC_TEST_LENGTH  64
#define VLT_MIN 100

hi_u16 g_adc_buf[ADC_TEST_LENGTH] = { 0 };

//
#include <stdio.h>
#include <unistd.h>

#include "ohos_init.h"
#include "cmsis_os2.h"

#include "wifi_device.h"
#include "lwip/netifapi.h"
#include "lwip/api_shell.h"
#include <netdb.h>
#include <string.h>
#include <stdlib.h>
#include "lwip/sockets.h"//套接字的头文件
#include "wifi_connect.h"

#define SERVER_IP "192.168.43.55"  // 服务器IP地址
#define SERVER_PORT 6000         // 服务器端口号


//



int key_status = KEY_EVENT_NONE;
char key_flg = 0;


int get_key_event(void)
{
    int tmp = key_status;
    key_status = KEY_EVENT_NONE;
    return tmp;
}

/* asic adc test  */
hi_void convert_to_voltage(hi_u32 data_len)
{
    hi_u32 i;
    float vlt_max = 0;
    float vlt_min = VLT_MIN;

    float vlt_val = 0;

    hi_u16 vlt;
    for (i = 0; i < data_len; i++) {
        vlt = g_adc_buf[i];
        float voltage = (float)vlt * 1.8 * 4 / 4096.0;  /* vlt * 1.8 * 4 / 4096.0: Convert code into voltage */
        vlt_max = (voltage > vlt_max) ? voltage : vlt_max;
        vlt_min = (voltage < vlt_min) ? voltage : vlt_min;
    }
    // printf("vlt_min:%.3f, vlt_max:%.3f \n", vlt_min, vlt_max);

    vlt_val = (vlt_min + vlt_max)/2.0;

    if((vlt_val > 0.4) && (vlt_val < 0.6))
    {
        if(key_flg == 0)
        {
            key_flg = 1;
            key_status = KEY_EVENT_S1;
        }
    }
    if((vlt_val > 0.8) && (vlt_val < 1.1))
    {
        if(key_flg == 0)
        {
            key_flg = 1;
            key_status = KEY_EVENT_S2;
        }
    }

    if((vlt_val > 0.01) && (vlt_val < 0.3))
    {
        if(key_flg == 0)
        {
            key_flg = 1;
            key_status = KEY_EVENT_S3;
        }
    }

    if(vlt_val > 3.0)
    {
        key_flg = 0;
        key_status = KEY_EVENT_NONE;
    }
}




void app_demo_adc_test(void)
{
    hi_u32 ret, i;
    hi_u16 data;  /* 10 */

    memset_s(g_adc_buf, sizeof(g_adc_buf), 0x0, sizeof(g_adc_buf));
 
    for (i = 0; i < ADC_TEST_LENGTH; i++) {
        ret = hi_adc_read((hi_adc_channel_index)HI_ADC_CHANNEL_2, &data, HI_ADC_EQU_MODEL_1, HI_ADC_CUR_BAIS_DEFAULT, 0);
        if (ret != HI_ERR_SUCCESS) {
            printf("ADC Read Fail\n");
            return;
        }
        g_adc_buf[i] = data;
    }
    convert_to_voltage(ADC_TEST_LENGTH);

}

/* 设置 按键中断响应 */
void my_gpio_isr_demo(void *arg)
{
    arg = arg;
    hi_u32 ret;

    printf("----- gpio isr demo -----\r\n");

    (hi_void)hi_gpio_init();
    
    hi_io_set_func(HI_IO_NAME_GPIO_5, HI_IO_FUNC_GPIO_5_GPIO); /* uart1 rx */

    ret = hi_gpio_set_dir(HI_GPIO_IDX_5, HI_GPIO_DIR_IN);
    if (ret != HI_ERR_SUCCESS) {
        printf("===== ERROR ======gpio -> hi_gpio_set_dir1 ret:%d\r\n", ret);
        return;
    }

    const char *message = "0";
    while(1)
    {
        //读取ADC值
        app_demo_adc_test();
        
        switch(get_key_event())
        {
            case KEY_EVENT_NONE:
            {
                // UDPClientFunction(message);//未触发时
                // printf("KEY_EVENT_NONE \r\n");
            }
            break;

            case KEY_EVENT_S1:
            {
                const char *message = "1"; // 要发送的消息
                UDPClientFunction(message);
                printf("KEY_EVENT_S1 \r\n");
            }
            break;

            case KEY_EVENT_S2:
            {
                const char *message = "3"; // 要发送的消息
                UDPClientFunction(message);
                printf("KEY_EVENT_S2 \r\n");
            }
            break;

            case KEY_EVENT_S3:
            {
                const char *message = "2"; // 要发送的消息
                UDPClientFunction(message);
                printf("KEY_EVENT_S3 \r\n");
            }
            break;

        }

        usleep(30000);
    }
    

}

void UDPClientFunction(const char *message)
{
    int sock_fd;
    struct sockaddr_in server_addr;

    // 创建socket
    if ((sock_fd = socket(AF_INET, SOCK_DGRAM, 0)) == -1)
    {
        perror("socket");
        return;
    }

    // 设置服务器地址信息
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    server_addr.sin_addr.s_addr = inet_addr(SERVER_IP);

    // 发送数据
    ssize_t ret = sendto(sock_fd, message, strlen(message), 0, (struct sockaddr *)&server_addr, sizeof(server_addr));
    if (ret == -1)
    {
        perror("sendto");
        close(sock_fd);
        return;
    }

    printf("Sent data: %s\n", message);

    close(sock_fd);
}


void key_demo(void)
{
    osThreadAttr_t attr;
    
    attr.name = "KeyTask";
    attr.attr_bits = 0U;
    attr.cb_mem = NULL;
    attr.cb_size = 0U;
    attr.stack_mem = NULL;
    attr.stack_size = 2048;
    attr.priority = 26;

    if (osThreadNew((osThreadFunc_t)my_gpio_isr_demo, NULL, &attr) == NULL) {
        printf("[key_demo] Falied to create KeyTask!\n");
    }
    
}


SYS_RUN(key_demo);

