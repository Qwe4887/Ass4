import socket


def start_server(host, port):
    # 创建一个UDP套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f"服务器已启动，监听端口 {port}...")

    while True:
        # 接收来自客户端的请求
        message, client_address = server_socket.recvfrom(1024)
        print(f"收到来自 {client_address} 的消息：{message.decode()}")

        # 解析请求内容
        request = message.decode().strip()

        if request.startswith("DOWNLOAD"):
            filename = request.split(" ")[1]
            # 检查文件是否存在（假设文件在当前目录）
            try:
                with open(filename, 'rb') as file:
                    # 如果文件存在，回应客户端文件的大小
                    file_size = len(file.read())
                    response = f"OK {filename} SIZE {file_size} PORT 50001"
                    server_socket.sendto(response.encode(), client_address)
                    print(f"文件 {filename} 存在，发送文件大小 {file_size} 到客户端")
            except FileNotFoundError:
                # 文件不存在，返回错误消息
                response = f"ERR {filename} NOT_FOUND"
                server_socket.sendto(response.encode(), client_address)
                print(f"文件 {filename} 不存在")


if __name__ == "__main__":
    host = "localhost"  # 服务器主机名
    port = 51234  # 监听端口
    start_server(host, port)
