import socket
import os
import threading

# 定义服务器地址和端口
HOST = 'localhost'
PORT = 51234

# 服务器提供的文件列表（可以在实际中更改或扩展）
available_files = {
    "file1.txt": 1234,  # 假设file1.txt文件大小为1234字节
    "file2.pdf": 5678,  # 假设file2.pdf文件大小为5678字节
}


# 处理单个客户端请求的函数
def handle_client(client_address, request, server_socket):
    if request.startswith("DOWNLOAD"):
        filename = request.split()[1]
        if filename in available_files:
            # 返回文件信息
            file_size = available_files[filename]
            response = f"OK {filename} SIZE {file_size} PORT 50001"
            server_socket.sendto(response.encode('utf-8'), client_address)

            # 开启新的端口和套接字传输文件
            file_transfer_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            file_transfer_server_socket.bind(('localhost', 50001))

            while True:
                data, _ = file_transfer_server_socket.recvfrom(1024)
                data_parts = data.decode('utf-8').split()

                # 处理文件请求
                if data_parts[0] == "FILE":
                    try:
                        start = int(data_parts[4])  # 获取START后的数字
                        end = int(data_parts[6])  # 获取END后的数字
                    except ValueError as e:
                        print(f"解析请求数据时发生错误: {e}")
                        break

                    file_data = read_file_chunk(filename, start, end)

                    # 返回文件数据
                    response = f"FILE {filename} OK START {start} END {end} DATA {file_data}"
                    file_transfer_server_socket.sendto(response.encode('utf-8'), client_address)

                    # 文件传输完毕
                    if end >= file_size:
                        break

                # 处理文件关闭请求
                elif data_parts[0] == "FILE" and data_parts[1] == filename and data_parts[2] == "CLOSE":
                    response = f"FILE {filename} CLOSE_OK"
                    file_transfer_server_socket.sendto(response.encode('utf-8'), client_address)
                    print(f"文件 {filename} 传输完毕，关闭连接。")
                    break

            file_transfer_server_socket.close()

        else:
            # 文件未找到
            response = f"ERR {filename} NOT_FOUND"
            server_socket.sendto(response.encode('utf-8'), client_address)
    else:
        print("无效请求")
        server_socket.sendto(b"ERR INVALID_REQUEST", client_address)


# 启动服务器
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 使用UDP
    server_socket.bind((HOST, PORT))  # 绑定服务器地址和端口
    print(f"服务器已启动，监听 {HOST}:{PORT}...")

    while True:
        # 接收客户端请求
        message, client_address = server_socket.recvfrom(1024)
        request = message.decode('utf-8').strip()

        # 启动新线程处理每个客户端请求
        client_thread = threading.Thread(target=handle_client, args=(client_address, request, server_socket))
        client_thread.start()


# 读取文件的特定字节块
def read_file_chunk(filename, start, end):
    with open(filename, 'rb') as f:
        f.seek(start)
        data = f.read(end - start + 1)
    return data.hex()


if __name__ == "__main__":
    start_server()
