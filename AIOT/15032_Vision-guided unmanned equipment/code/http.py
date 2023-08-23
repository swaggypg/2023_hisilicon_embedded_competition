import io
import socket
import struct
import queue
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from picamera import PiCamera
from PIL import Image, ImageDraw

# 设置树莓派摄像头分辨率和帧率
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FRAMERATE = 60

# 设置三等分红框的宽度
BOX_WIDTH = CAMERA_WIDTH // 3

# 定义HTTP服务器地址和端口
SERVER_IP = "192.168.43.55"
SERVER_PORT = 8081

# 创建摄像头对象
camera = PiCamera(resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=CAMERA_FRAMERATE)

# 创建一个锁，用于控制视频帧的访问
frame_lock = threading.Lock()

# 创建一个全局变量，用于存储红框类型
red_box_type = None

# 创建HTTP请求处理器
class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global red_box_type

        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()

            try:
                while True:
                    frame = get_frame_with_red_box()
                    self.send_frame(frame)

            except KeyboardInterrupt:
                pass
            return

    def send_frame(self, frame):
        self.wfile.write(b'--jpgboundary')
        self.send_header('Content-type', 'image/jpeg')
        self.send_header('Content-length', len(frame))
        self.end_headers()
        self.wfile.write(frame)

# 获取视频帧并加入红框
def get_frame_with_red_box():
    global red_box_type

    stream = io.BytesIO()
    with frame_lock:
        camera.capture(stream, format='jpeg', use_video_port=True)
        image = Image.open(stream)

        # 根据红框类型在图像上添加红框
        if red_box_type == 'a' or red_box_type == 'A':
            draw_box(image, 0,"red")
        elif red_box_type == 'w' or red_box_type == 'W':
            draw_box(image, BOX_WIDTH,"red")
        elif red_box_type == 'd' or red_box_type == 'D':
            draw_box(image, 2 * BOX_WIDTH,"red")
        # 根据绿框类型在图像上添加绿框
        if red_box_type == 'f' or red_box_type == 'F':
            draw_box(image, 0,"green")
        elif red_box_type == 'T' or red_box_type == 't':
            draw_box(image, BOX_WIDTH,"green")
        elif red_box_type == 'H' or red_box_type == 'h':
            draw_box(image, 2 * BOX_WIDTH,"green")
        # 根据蓝框类型在图像上添加蓝框
        if red_box_type == 'j' or red_box_type == 'J':
            draw_box(image, 0,"blue")
        elif red_box_type == 'I' or red_box_type == 'i':
            draw_box(image, BOX_WIDTH,"blue")
        elif red_box_type == 'l' or red_box_type == 'L':
            draw_box(image, 2 * BOX_WIDTH,"blue")





        # 转换图像格式为JPEG并返回
        jpeg_image = io.BytesIO()
        image.save(jpeg_image, 'JPEG')
        return jpeg_image.getvalue()

# 在图像上绘制红框
def draw_box(image, x, color):
    draw = ImageDraw.Draw(image)
    draw.rectangle([(x, 0), (x + BOX_WIDTH, CAMERA_HEIGHT)], outline=color, width=4)

# UDP接收线程
red_box_type = None
data_queue = queue.Queue()
def udp_listener():
    global red_box_type

    UDP_IP = "0.0.0.0"
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024)
        red_box_type = data.decode()
        data_queue.put(red_box_type)
    # UDP_IP = "0.0.0.0"
    # UDP_PORT = 5005

    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.bind((UDP_IP, UDP_PORT))

    # while True:
    #     data, addr = sock.recvfrom(1024)
    #     red_box_type = data.decode()
should_exit = False
def get_user_input():
    global should_exit

    while not should_exit:
        user_input = input("输入 q 停止程序：")
        if user_input.lower() == 'q':
            should_exit = True
            break
    # 当用户输入 'q' 时，退出程序
    print("正在停止程序...")
    # 停止HTTP服务器
    http_server.shutdown()
    
if __name__ == '__main__':
    udp_thread = threading.Thread(target=udp_listener)
    udp_thread.start()

    # 启动用户输入监听线程
    user_input_thread = threading.Thread(target=get_user_input)
    user_input_thread.start()

    # 启动HTTP服务器
    server_address = (SERVER_IP, SERVER_PORT)
    http_server = HTTPServer(server_address, HTTPRequestHandler)
    print('Starting HTTP server...')
    http_server.serve_forever()
    print('Stopping HTTP server...')
   
    # 等待用户输入监听线程结束
    user_input_thread.join()

    # 关闭摄像头资源
    print('Stopping HTTP server...')
    camera.close()
