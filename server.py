import socket

# 定义服务器地址和端口
HOST = 'localhost'
PORT = 51234

# 服务器提供的文件列表（可以在实际中更改或扩展）
available_files = {
    "file1.txt": 1234,  # 假设file1.txt文件大小为1234字节
    "file2.pdf": 5678,  # 假设file2.pdf文件大小为5678字节
}


# 启动服务器
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 使用UDP
    server_socket.bind((HOST, PORT))  # 绑定服务器地址和端口
    print(f"服务器已启动，监听 {HOST}:{PORT}...")

    while True:
        # 接收客户端请求
        message, client_address = server_socket.recvfrom(1024)
        request = message.decode('utf-8').strip()

        print(f"收到来自 {client_address} 的请求: {request}")

        # 处理请求
        if request.startswith("DOWNLOAD"):
            filename = request.split()[1]
            if filename in available_files:
                # 返回文件信息
                file_size = available_files[filename]
                response = f"OK {filename} SIZE {file_size} PORT 50001"
            else:
                # 文件未找到
                response = f"ERR {filename} NOT_FOUND"

            server_socket.sendto(response.encode('utf-8'), client_address)  # 发送响应
        else:
            print("无效请求")
            server_socket.sendto(b"ERR INVALID_REQUEST", client_address)


# 启动服务器
if __name__ == "__main__":
    start_server()
