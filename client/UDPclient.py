import socket


def send_request(server_host, server_port, filename):
    # 创建UDP套接字
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 发送下载请求
    download_request = f"DOWNLOAD {filename}"
    client_socket.sendto(download_request.encode(), (server_host, server_port))
    print(f"Sent request: {download_request}")

    # 等待并接收服务器的响应
    response, server_address = client_socket.recvfrom(1024)
    print(f"Received response: {response.decode()} from {server_address}")

    # 判断响应类型
    if response.decode().startswith("OK"):
        print(f"File {filename} is available, size and port received.")
    else:
        print(f"Error: {response.decode()}")


if __name__ == "__main__":
    send_request("localhost", 51234, "example.txt")
