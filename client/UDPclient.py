import socket


def start_client(server_host, server_port, filename):
    # 创建一个UDP套接字
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(5)  # 设置超时时间为5秒

    # 发送下载请求
    download_request = f"DOWNLOAD {filename}"
    client_socket.sendto(download_request.encode(), (server_host, server_port))
    print(f"向服务器发送下载请求：{download_request}")

    try:
        # 等待服务器回应
        response, _ = client_socket.recvfrom(1024)
        response_message = response.decode().strip()
        print(f"收到服务器响应：{response_message}")

        # 解析响应内容
        if response_message.startswith("OK"):
            # 服务器返回OK，获取文件大小和端口号
            parts = response_message.split()
            file_size = int(parts[3])
            server_port = int(parts[5])
            print(f"文件大小：{file_size} bytes，文件传输端口：{server_port}")
        elif response_message.startswith("ERR"):
            # 文件未找到
            print("错误：文件未找到！")
    except socket.timeout:
        print("请求超时，未收到服务器响应。")


if __name__ == "__main__":
    server_host = "localhost"  # 服务器主机名
    server_port = 51234  # 服务器端口
    filename = "example.txt"  # 要下载的文件名
    start_client(server_host, server_port, filename)
