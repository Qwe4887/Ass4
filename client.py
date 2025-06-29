import socket

# 定义客户端连接的服务器地址和端口
HOST = 'localhost'
PORT = 51234

# 向服务器发送请求并接收响应
def send_request(filename):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 使用UDP

    # 发送下载请求
    request = f"DOWNLOAD {filename}"
    client_socket.sendto(request.encode('utf-8'), (HOST, PORT))

    # 接收服务器响应
    response, _ = client_socket.recvfrom(1024)
    response_message = response.decode('utf-8')
    print(f"收到服务器响应: {response_message}")

    # 关闭客户端套接字
    client_socket.close()

# 主程序
if __name__ == "__main__":
    filename_to_download = "file1.txt"  # 要请求的文件名
    send_request(filename_to_download)
