import socket

def start_server(host, port):
    # 创建UDP套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f"Server is listening on {host}:{port}")

    while True:
        # 等待接收客户端请求
        message, client_address = server_socket.recvfrom(1024)  # 接收数据
        print(f"Received message: {message.decode()} from {client_address}")

        # 处理客户端请求
        if message.decode().startswith("DOWNLOAD"):
            filename = message.decode().split(" ")[1]
            try:
                # 检查文件是否存在
                with open(filename, "rb") as f:
                    file_size = len(f.read())
                    print(f"Sending file size {file_size} for {filename}")
                    # 回复文件大小信息
                    response = f"OK {filename} SIZE {file_size} PORT 50001"
                    server_socket.sendto(response.encode(), client_address)
            except FileNotFoundError:
                print(f"File {filename} not found.")
                response = f"ERR {filename} NOT_FOUND"
                server_socket.sendto(response.encode(), client_address)

if __name__ == "__main__":
    start_server("localhost", 51234)
