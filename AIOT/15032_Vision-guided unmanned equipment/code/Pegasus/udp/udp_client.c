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

#define _PROT_ 5566//端口对应上面的“8888”

//在sock_fd 进行监听，在 new_fd 接收新的链接
int sock_fd;

int addr_length;
static const char *send_data = "Hello! I'm UDP Test!\r\n";

static void UDPClientTask(void)
{
    //初始化服务器的地址信息的结构体
    struct sockaddr_in send_addr;
    socklen_t addr_length = sizeof(send_addr);
    char recvBuf[512];

    //连接Wifi
    WifiConnect("EVA_AL00", "123..321");//修改成和自己电脑一致的SSID与password
    //创建本机的套接字socket（一对中的其一）
    if ((sock_fd = socket(AF_INET, SOCK_DGRAM, 0)) == -1)
    {
        perror("create socket failed!\r\n");
        exit(1);
    }

    //初始化预连接的服务端地址，绑定服务端的IP以及应用进程端口
    //IPV4
    send_addr.sin_family = AF_INET;
    //通信另一端的应用进程端口
    send_addr.sin_port = htons(_PROT_);
    //通信另一端的IP地址
    send_addr.sin_addr.s_addr = inet_addr("192.168.43.55");
    addr_length = sizeof(send_addr);

    //总计发送 count 次数据
    while (1)
    {
        bzero(recvBuf, sizeof(recvBuf));

        //发送数据到服务远端
        sendto(sock_fd, send_data, strlen(send_data), 0, (struct sockaddr *)&send_addr, addr_length);

        //线程休眠一段时间
        sleep(10);

        //接收服务端返回的字符串
        recvfrom(sock_fd, recvBuf, sizeof(recvBuf), 0, (struct sockaddr *)&send_addr, &addr_length);
        printf("%s:%d=>%s\n", inet_ntoa(send_addr.sin_addr), ntohs(send_addr.sin_port), recvBuf);
    }

    //关闭这个 socket
    closesocket(sock_fd);
}

static void UDPClientDemo(void)
{
    osThreadAttr_t attr;

    attr.name = "UDPClientTask";
    attr.attr_bits = 0U;
    attr.cb_mem = NULL;
    attr.cb_size = 0U;
    attr.stack_mem = NULL;
    attr.stack_size = 10240;
    attr.priority = osPriorityNormal;

    if (osThreadNew((osThreadFunc_t)UDPClientTask, NULL, &attr) == NULL)
    {
        printf("[UDPClientDemo] Falied to create UDPClientTask!\n");
    }
}

APP_FEATURE_INIT(UDPClientDemo);
