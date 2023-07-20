/*
 * Copyright (c) 2020 Nanjing Xiaoxiongpai Intelligent Technology Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <stdio.h>
#include <unistd.h>
#include "ohos_init.h"
#include "cmsis_os2.h"

#include "lwip/sockets.h"
#include "wifi_connect.h"

#define _PROT_ 8888

//在sock_fd 进行监听，在 new_fd 接收新的链接
int sock_fd;

char recvbuf[512];
char *buf = "Hello! I'm Pegasus UDP Server!";
char *serverC_ip = "192.168.43.55";  // 服务器C的IP地址
int serverC_port = 5566;              // 服务器C的端口号

static void UDPServerTask(void)
{
    // 服务端地址信息
    struct sockaddr_in server_sock;

    // 客户端地址信息
    struct sockaddr_in client_sock;
    int sin_size;

    // 连接Wifi
    WifiConnect("EVA_AL00", "123..321");

    // 创建socket
    if ((sock_fd = socket(AF_INET, SOCK_DGRAM, 0)) == -1)
    {
        perror("socket is error\r\n");
        exit(1);
    }

    bzero(&server_sock, sizeof(server_sock));
    server_sock.sin_family = AF_INET;
    server_sock.sin_addr.s_addr = htonl(INADDR_ANY);
    server_sock.sin_port = htons(_PROT_);

    // 调用bind函数绑定socket和地址
    if (bind(sock_fd, (struct sockaddr *)&server_sock, sizeof(struct sockaddr)) == -1)
    {
        perror("bind is error\r\n");
        exit(1);
    }

    while (1)
    {
        sin_size = sizeof(struct sockaddr_in);

        // 接收来自客户端A的数据
        ssize_t ret;
        if ((ret = recvfrom(sock_fd, recvbuf, sizeof(recvbuf), 0, (struct sockaddr *)&client_sock, (socklen_t *)&sin_size)) == -1)
        {
            printf("recv error \r\n");
        }
        printf("Received data from client A: %s\r\n", recvbuf);

        // TestGpioInit();
        // currentType = SetKeyType(KEY_UP);
        // while (1) {
        // switch (GetKeyStatus(CURRENT_MODE)) {

        // }
        
        
        // 将数据转发给服务器C
        struct sockaddr_in serverC_sock;
        bzero(&serverC_sock, sizeof(serverC_sock));
        serverC_sock.sin_family = AF_INET;
        serverC_sock.sin_addr.s_addr = inet_addr(serverC_ip);
        serverC_sock.sin_port = htons(serverC_port);

        if ((ret = sendto(sock_fd, recvbuf, strlen(recvbuf), 0, (struct sockaddr *)&serverC_sock, sizeof(serverC_sock))) == -1)
        {
            perror("sendto: ");
        }
        // printf("Forwarded data to server C\r\n");
    }

    close(sock_fd);
}

static void UDPServerDemo(void)
{
    osThreadAttr_t attr;

    attr.name = "UDPServerTask";
    attr.attr_bits = 0U;
    attr.cb_mem = NULL;
    attr.cb_size = 0U;
    attr.stack_mem = NULL;
    attr.stack_size = 10240;
    attr.priority = osPriorityNormal;

    if (osThreadNew((osThreadFunc_t)UDPServerTask, NULL, &attr) == NULL)
    {
        printf("[UDPServerDemo] Failed to create UDPServerTask!\n");
    }
}

APP_FEATURE_INIT(UDPServerDemo);
