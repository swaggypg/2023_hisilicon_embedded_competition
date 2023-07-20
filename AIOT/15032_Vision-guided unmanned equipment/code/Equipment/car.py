# -*- coding: utf-8 -*-                         #通过声明可以在程序中书写中文
import RPi.GPIO as GPIO                         #引入RPi.GPIO库函数命名为GPIO
import time                                     #引入计时time函数
import readchar
import socket
import io
# from PIL import Image, ImageDraw
# import cv2
# import numpy as np

import threading
#接口定义
INT1 = 11                                       #将L298 INT1口连接到树莓派Pin11
INT2 = 12                                       #将L298 INT2口连接到树莓派Pin12
INT3 = 13                                       #将L298 INT3口连接到树莓派Pin13
INT4 = 15                                       #将L298 INT4口连接到树莓派Pin15
ENA = 16                                        #将L298 ENA口连接到树莓派Pin16
ENB = 18                                        #将L298 ENB口连接到树莓派Pin18

def init():                                     #定义一个初始化函数
        GPIO.setmode(GPIO.BOARD)                #将GPIO编程方式设置为BOARD模式
        GPIO.setup(INT1,GPIO.OUT)               #将相应接口设置为输出模式
        GPIO.setup(INT2,GPIO.OUT)
        GPIO.setup(INT3,GPIO.OUT)
        GPIO.setup(INT4,GPIO.OUT)
        GPIO.setup(ENA,GPIO.OUT)
        GPIO.setup(ENB,GPIO.OUT)
def back():                                  #定义前进函数
        GPIO.output(INT1,GPIO.HIGH)             #将INT1接口设置为高电压
        GPIO.output(INT2,GPIO.LOW)             #将INT2接口设置为低电压
        GPIO.output(INT3,GPIO.HIGH)             #将INT3接口设置为高电压
        GPIO.output(INT4,GPIO.LOW)              #将INT4接口设置为低电压
        GPIO.cleanup()                          #释放配置过的gpio

def forward():                                     #定义后退函数
        GPIO.output(INT1,GPIO.LOW)
        GPIO.output(INT2,GPIO.HIGH)
        GPIO.output(INT3,GPIO.LOW)
        GPIO.output(INT4,GPIO.HIGH)
        GPIO.cleanup()

def right():                                     #定义左转函数
        GPIO.output(INT1,GPIO.HIGH)
        GPIO.output(INT2,GPIO.LOW)
        GPIO.output(INT3,GPIO.LOW)
        GPIO.output(INT4,GPIO.HIGH)
        GPIO.cleanup()

def left():                                    #定义右转函数
        GPIO.output(INT1,GPIO.LOW)
        GPIO.output(INT2,GPIO.HIGH)
        GPIO.output(INT3,GPIO.HIGH)
        GPIO.output(INT4,GPIO.LOW)
        GPIO.cleanup()

def stop():                                     #定义停止函数
        GPIO.output(INT1,GPIO.LOW)
        GPIO.output(INT2,GPIO.LOW)
        GPIO.output(INT3,GPIO.LOW)
        GPIO.output(INT4,GPIO.LOW)
        GPIO.cleanup()

def contral(res):
        if (res == "W" or res =="w"):
                # add_bounding_box_to_motion_stream(server_address, 160, 0, 320, 360)
                print(res)
                forward()
                init()
                pwma.start(40)
                pwmb.start(40)
        elif (res == "d" or res =="D"):
                # add_bounding_box_to_motion_stream(server_address, 320, 0, 480, 360)
                print(res)
                right()
                init()
                pwma.start(23)
                pwmb.start(0)
        elif (res == "s" or res =="S"):
                print(res)
                back()
                init()
                pwma.start(40)
                pwmb.start(40)
        elif (res == "e" or res =="E"):
                print(res)
                right()
                init()
                pwma.start(25)
                pwma.start(25)
        elif (res == "q" or res =="Q"):
                print(res)
                left()
                init()
                pwma.start(25)
                pwmb.start(25)
        elif (res == "a" or res =="A"):
                # add_bounding_box_to_motion_stream(server_address, 0, 0, 160, 360)
                print(res)
                left()
                init()
                pwma.start(0)
                pwmb.start(23)
        else:
                print(res)
                stop()
                init()
                pwma.start(0)
                pwmb.start(0)

# def draw_bounding_box(image, x1, y1, x2, y2):
#     # 创建一个PIL Image对象
#     pil_image = Image.fromarray(image)

#     # 使用ImageDraw绘制矩形框
#     draw = ImageDraw.Draw(pil_image)
#     draw.rectangle([x1, y1, x2, y2], outline="red", width=10)

#     # 将修改后的图像转换回NumPy数组
#     modified_image = np.array(pil_image)

#     return modified_image

# def add_bounding_box_to_motion_stream(server_address, x1, y1, x2, y2):
#     # 创建一个UDP socket来连接到Motion服务器
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     client_socket.connect(server_address)

#     # 循环从Motion服务器接收图像
#     while True:
#         try:
#             # 接收图像数据
#             image_data, _ = client_socket.recvfrom(8081)

#             # 将图像数据转换为NumPy数组
#             image_np = np.frombuffer(image_data, dtype=np.uint8)

#             # 解码图像
#             image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

#             # 在图像上绘制框体
#             image_with_box = draw_bounding_box(image, x1, y1, x2, y2)

#             # 将图像转换回字节流
#             _, image_data = cv2.imencode('.jpg', image_with_box)
#             image_bytes = image_data.tobytes()

#             # 发送修改后的图像数据给Motion服务器
#             client_socket.sendall(image_bytes)

#         except KeyboardInterrupt:
#             # 用户按下Ctrl+C时退出循环
#             break

#     # 关闭socket
#     client_socket.close()

init()                                          #调用初始化程序，进行初始化
pwma = GPIO.PWM(ENA,80)                         #创建一个pwma实例，控制左电机转速。两个参数：1、GPIO引脚（ENA即为引脚16）；2、频率（设置为80）
pwmb = GPIO.PWM(ENB,80)                         #创建一个pwmb实例，控制右电机转速。
pwma.start(0)                                   #以输出0%占空比开始
pwmb.start(0)
# server_address = ('localhost', 8081)
# 创建UDP套接字
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 绑定IP地址和端口号
ip_address = '0.0.0.0'  # 监听所有网络接口的IP地址
port = 5566  # 选择一个可用的端口号
udp_socket.bind((ip_address, port))

print(f"UDP socket listening on {ip_address}:{port}")

udp_socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 绑定IP地址和端口号
ip_address1 = '0.0.0.0'  # 监听所有网络接口的IP地址
port1 = 6000  # 选择一个可用的端口号
udp_socket1.bind((ip_address1, port1))
print(f"UDP socket listening on {ip_address1}:{port1}")
auto = ""
while 1:                                        #1为真，永远成立，程序一直执行
        
        
        
        res, address = udp_socket.recvfrom(1024)  # 指定接收的数据缓冲区大小
        res = str(res,"utf-8")
        # print(type(res),res)
        # keyinput = readchar.readkey()
        Auto = ["Keep","Semi-Auto","Retreat","Stop"]
        res1, address1 = udp_socket1.recvfrom(1024)  # 指定接收的数据缓冲区大小
        res1 = str(res1,"utf-8")
        
        if res1 == "2":
                print("Move:",res,"   mode:",Auto[int(res1)])
                back()
                init()
                pwma.start(40)
                pwmb.start(40)
        elif res1 == "3":
                print("Move: None mode:",Auto[int(res1)])
                stop()
                init()
                pwma.start(0)
                pwmb.start(0)
        else:
                print("Move:",res,"   mode:",Auto[int(res1)])
                if res != None and res1 == "1":
                        contral(res)

        
                
                
udp_socket1.close()                
# 关闭套接字
udp_socket.close()
