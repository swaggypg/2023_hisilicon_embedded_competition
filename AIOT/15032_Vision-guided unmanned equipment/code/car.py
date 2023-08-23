import queue
import select
import socket
import RPi.GPIO as GPIO  
import multiprocessing
from time import sleep
import time
import threading

#接口定义
TRIG = 35					#将超声波模块TRIG口连接到树莓派Pin35
ECHO = 37                                        #将超声波模块ECHO口连接到树莓派Pin37
INT1 = 11                                       #将L298 INT1口连接到树莓派Pin11
INT2 = 12                                       #将L298 INT2口连接到树莓派Pin12
INT3 = 13                                       #将L298 INT3口连接到树莓派Pin13
INT4 = 15                                       #将L298 INT4口连接到树莓派Pin15
ENA = 16                                        #将L298 ENA口连接到树莓派Pin16
ENB = 18                                        #将L298 ENB口连接到树莓派Pin18

def init():                                     #定义一个初始化函数
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)                #将GPIO编程方式设置为BOARD模式
        #超声波传感器引脚初始化
        GPIO.setup(TRIG,GPIO.OUT) #将发射端引脚设置为输出
        GPIO.setup(ECHO,GPIO.IN) #将接收端引脚设置为输入
        GPIO.setup(INT1,GPIO.OUT)               #将相应接口设置为输出模式
        GPIO.setup(INT2,GPIO.OUT)
        GPIO.setup(INT3,GPIO.OUT)
        GPIO.setup(INT4,GPIO.OUT)
        GPIO.setup(ENA,GPIO.OUT)
        GPIO.setup(ENB,GPIO.OUT)

#超声波测距函数
def Distance_Ultrasound():
    emitTime = 0  # 初始化发射时间
    acceptTime = 0  # 初始化接收时间
    GPIO.output(TRIG,GPIO.LOW)		#输出口初始化置LOW（不发射）
    time.sleep(0.000002)
    GPIO.output(TRIG,GPIO.HIGH)		#发射超声波
    time.sleep(0.00001)
    GPIO.output(TRIG,GPIO.LOW)		#停止发射超声波
    while GPIO.input(ECHO) == 0:
        emitTime = time.time()		#记录发射时间
    while GPIO.input(ECHO) == 1:
        acceptTime = time.time()	#记录接收时间
    totalTime = acceptTime - emitTime		#计算总时间
    distanceReturn = totalTime * 340 / 2 * 100  	#计算距离（单位：cm）
    return  distanceReturn			#返回距离

#避障函数
def Obstacle_Avoidance():
        while True:
                dis = Distance_Ultrasound()
                print("距离 ",dis,"cm")
                if dis < 30:				#距离小于30cm时启动避障程序
                        while dis < 30:
                                Back_time(0.5)		#距离小于30cm时后退0.5s
                                dis = Distance_Ultrasound()
                                print("距离 ",dis,"cm")
                Left_time(1.5)			#左转1.5s
                Forward()				#继续前进
                time.sleep(0.5)

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

def operation_contral(res):
        # print("operation_contral")

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
                pwma.start(40)
                pwmb.start(40)
                sleep(0.55)
                stop()
                init()
                pwma.start(0)
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
                pwma.start(40)
                pwmb.start(40)
                sleep(0.55)
                stop()
                init()
                pwma.start(0)
                pwmb.start(0)
        else:
                print(res,"+")
                stop()
                init()
                pwma.start(0)
                pwmb.start(0)

def operation_contral_DU(res):
        # print("operation_contral")

        
        if (res == "d" or res =="D"):
                # add_bounding_box_to_motion_stream(server_address, 320, 0, 480, 360)
                print(res)
                right()
                init()
                pwma.start(40)
                pwmb.start(40)
                sleep(0.55)
                stop()
                init()
                pwma.start(0)
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
                pwma.start(40)
                pwmb.start(40)
                sleep(0.55)
                stop()
                init()
                pwma.start(0)
                pwmb.start(0)
        else:
                print(res,"+")
                stop()
                init()
                pwma.start(0)
                pwmb.start(0)

def speed_contral(res):
        # print("speed_contral")
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
                # right()
                forward()
                init()
                pwma.start(20)
                pwmb.start(40)
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
                # left()
                forward()
                init()
                pwma.start(40)
                pwmb.start(20)
        else:
                print(res,"-")
                stop()
                init()
                pwma.start(0)
                pwmb.start(0)


init()                                          #调用初始化程序，进行初始化
pwma = GPIO.PWM(ENA,80)                         #创建一个pwma实例，控制左电机转速。两个参数：1、GPIO引脚（ENA即为引脚16）；2、频率（设置为80）
pwmb = GPIO.PWM(ENB,80)                         #创建一个pwmb实例，控制右电机转速。
pwma.start(0)                                   #以输出0%占空比开始
pwmb.start(0)
# 代码段A
def code_segment_A(move):
    print("Executing Code Segment A:move",move)

# 代码段B
def code_segment_B(data,model):
        if model == "operation":
                pass
        elif model == "speed":
                data = speed_list[data]
        elif model == "stop":
                data == stop_list[data]
        elif model == "normal":
                pass
        if data is not None:
                UDP_IP = "192.168.43.55"
                UDP_PORT = 5005

                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(data.encode(), (UDP_IP, UDP_PORT))
                sock.close()
        # print(f"Received data from 5566: {data},and uploading")

# UDP监听函数
def udp_listener(port, queue):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('0.0.0.0', port))
    # print(f"UDP socket listening on 0.0.0.0:{port}")

    while True:
        data, address = udp_socket.recvfrom(1024)
        # print(f"Received data from {address}: {data.decode()}")
        data = str(data,"utf-8")
        queue.put(data)  # 将接收到的数据放入队列

# 并发执行的函数
def concurrent_function(queue):
    while True:
        dis = Distance_Ultrasound()
        # print("距离", dis, "cm")
        time.sleep(0.5)
        queue.put(dis)

if __name__ == "__main__":
    # 创建一个进程间通信的队列
    data_queue1 = multiprocessing.Queue()
    data_queue2 = multiprocessing.Queue()
    du_queue = multiprocessing.Queue()
    # 创建进程a，监听6000端口的UDP信号
    process_a = multiprocessing.Process(target=udp_listener, args=(6000, data_queue1))
    process_a.start()

    # 创建进程b，监听5566端口的UDP信号
    process_b = multiprocessing.Process(target=udp_listener, args=(5566, data_queue2))
    process_b.start()

    # 创建进程b，监听5566端口的UDP信号
    process_du = multiprocessing.Process(target=concurrent_function, args=(du_queue,))
    process_du.start()
    # 主进程（或其他进程c）持续监听队列，直到接收到来自6000端口的UDP信号后，执行代码段A
    # 标志位，控制程序运行状态
    model = 1
    state = 1
    i = 0 
    data_from_q1 = None
    data_from_q2 = None
    du = None
    DU = None
    speed_list = {"a":"f","w":"t","d":"h"," ":"z"}
    stop_list = {"a":"j","w":"i","d":"l"," ":"x"}

    while True:

        try:
            data_from_q1 = data_queue1.get_nowait()
        except queue.Empty:
            data_from_q1 = None
        
        try:
            data_from_q2 = data_queue2.get_nowait()
        except queue.Empty:
            pass
        
        try:
            du = du_queue.get_nowait()
        except queue.Empty:
            pass
        if du:
                print("距离:", du, "cm")
                if du >= 35:
                        DU = 1
                else:
                        
                        DU = 0
                        operation_contral_DU(data_from_q2)
                        data_from_q2 = None
        if data_from_q1 == "3":
               state = 1
        elif data_from_q1 == "1":
                i += 1
                print(i,"------------------------")
                state = 2
        elif data_from_q1 == "2":
               state = 0
        if i % 2 == 0 and state != 0: # operation
                # print("model1——————————————————————————")
                if data_from_q1 == "3" and data_from_q2 is not None:
                        print("______________operation_model")
                        # code_segment_B("data_from_q2")
                        
                        operation_contral(data_from_q2) # model 1 operation mode
                        
                        # code_segment_B(data_from_q2,"operation")
                        # data_from_q2 = None
        if i % 2 != 0 and state == 1:# speed
                print("****************************speed_model")
                if DU == 1:
                        speed_contral(data_from_q2)
                elif DU == 0:
                        print("避障")
                        operation_contral_DU(data_from_q2)
                # code_segment_B(data_from_q2,"speed")
        if state == 0:
                print("=====================================================stop_model")
                stop()
                init()
                pwma.start(0)
                pwmb.start(0)
                # code_segment_B(data_from_q2,"stop")
                # data_from_q2 = None
        if i % 2 == 0 and data_from_q2:
                code_segment_B(data_from_q2,"operation")
        if i % 2 != 0 and data_from_q2:
                code_segment_B(data_from_q2,"speed")
        
        # if data_from_q1 == "1":
        #        model = 1
        # if data_from_q1 == "2":
        #         i += 1
        # if model != 3:
        #         if i % 2 != 0:
        #                 model = 2
        #         if i % 2 == 0:
        #                 model = 1

        # if data_from_q1 == "3":
        #        model = 3
       
        # if model == 1:
        #         # print("model1——————————————————————————")
        #         if data_from_q1 == "1" and data_from_q2 is not None:
        #                 print("___________________________operation_model")
        #                 # code_segment_B("data_from_q2")
        #                 operation_contral(data_from_q2) # model 1 operation mode
        # if model == 2: # model 2 Speed mode
        #         print("speed_model",data_from_q2)

        #         speed_contral(data_from_q2)
        # if model == 3: # model 3 stop
        #         print("stop_model")
        #         stop()
        #         init()
        #         pwma.start(0)
        #         pwmb.start(0)
        
        # code_segment_B(data_from_q2)
        # sleep()
        # break
        # print("______",data_from_q2)



#  # 主进程持续监听队列，直到接收到来自6000端口的UDP信号后，执行代码段A
#     while True:
#         # 使用select模块监听多个队列
#         readables, _, _ = select.select([data_queue1, data_queue2], [], [])

#         for queue in readables:
#             if queue == data_queue1:
#                 data_from_q1 = data_queue1.get()
#                 if data_from_q1 == "2":  
#                     model += 1

#                 if model % 2 != 0: # model 2 Speed mode
#                     speed_contral(data_from_q2)
#                 if data_from_q1 == "3": # model 3 stop
#                     # print("stop")
#                     stop()
#                     init()
#                     pwma.start(0)
#                     pwmb.start(0)
#                 if model % 2 == 0:
#                     if data_from_q1 == "1" and data_from_q2 is not None:
#                         # print("Straight")
#                         operation_contral(data_from_q2) # model 1 operation mode
#             elif queue == data_queue2:
#                 data_from_q2 = data_queue2.get()
#                 # print(data_from_q2)
#                 code_segment_B(data_from_q2)

        
