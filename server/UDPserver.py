import socket
import os
import base64
import threading


# 服务器函数，用于处理数据传输
def handle_file_transfer(client_socket, file_name, file_size, client_address):
    # 为每个文件请求创建独立的端口和套接字
    transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    transfer_port = 50000  # 固定端口（可以随机生成）
    transfer_socket.bind(('0.0.0.0', transfer_port))

    # 向客户端发送 OK 消息，包括文件大小和传输端口
    ok_message = f"OK {file_name} SIZE {file_size} PORT {transfer_port}"
    client_socket.sendto(ok_message.encode(), client_address)

    with open(file_name, 'rb') as f:
        while True:
            data, _ = transfer_socket.recvfrom(1024)
            request = data.decode()
            if 'GET START' in request:
                parts = request.split()
                start = int(parts[4])
                end = int(parts[6])

                # 从文件中读取指定字节
                f.seek(start)
                file_data = f.read(end - start)

                # 将二进制数据转换为Base64字符串
                base64_data = base64.b64encode(file_data).decode()

                # 发送数据给客户端
                response_message = f"FILE {file_name} OK START {start} END {end} DATA {base64_data}"
                transfer_socket.sendto(response_message.encode(), client_address)

                if end >= file_size:
                    break

    # 传输完成，发送关闭信息
    transfer_socket.sendto(f"FILE {file_name} CLOSE_OK".encode(), client_address)
    transfer_socket.close()


def udp_server(listen_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', listen_port))
    print(f"Server listening on port {listen_port}...")

    while True:
        message, client_address = server_socket.recvfrom(1024)
        print(f"Received message: {message.decode()} from {client_address}")

        request = message.decode().split()
        if request[0] == 'DOWNLOAD' and len(request) == 2:
            file_name = request[1]

            if os.path.exists(file_name):
                file_size = os.path.getsize(file_name)
                threading.Thread(target=handle_file_transfer,
                                 args=(server_socket, file_name, file_size, client_address)).start()
            else:
                response = f"ERR {file_name} NOT_FOUND"
                server_socket.sendto(response.encode(), client_address)
        else:
            print(f"Invalid request: {message.decode()}")


if __name__ == "__main__":
    listen_port = 51234
    udp_server(listen_port)
