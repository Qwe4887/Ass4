import socket
import base64


# 客户端发送消息并接收响应的重传机制
def send_and_receive(client_socket, message, server_ip, server_port, timeout, retries=5):
    attempt = 0
    while attempt < retries:
        try:
            # 发送请求
            client_socket.sendto(message.encode(), (server_ip, server_port))
            print(f"Sent message: {message}")

            # 等待响应
            client_socket.settimeout(timeout)  # 设置超时时间
            response, _ = client_socket.recvfrom(2048)  # 接收响应
            return response.decode()  # 返回响应数据

        except socket.timeout:
            attempt += 1
            print(f"Timeout occurred. Retrying... ({attempt}/{retries})")
            timeout *= 2  # 增加超时时间

    return None  # 如果超时多次仍然没有响应，返回 None


# 客户端处理文件下载的函数
def download_file(server_ip, server_port, filename):
    # 为每个文件创建独立的 UDP 套接字
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 发送下载请求
    message = f'DOWNLOAD {filename}'

    # 等待服务器响应（重传机制）
    response = send_and_receive(client_socket, message, server_ip, server_port, timeout=2)

    if response is None:
        print("Failed to receive a response from the server.")
        client_socket.close()
        return

    print(f"Received response: {response}")

    # 解析服务器的响应
    if response.startswith('OK'):
        parts = response.split()
        file_size = int(parts[3])  # 'SIZE'后面是文件大小
        transfer_port = int(parts[5])  # 'PORT'后面是端口号

        # 创建文件以保存下载的数据
        with open(f"downloaded_{filename}", 'wb') as f:
            received_data = 0
            while received_data < file_size:
                start = received_data
                end = min(start + 1000, file_size)  # 每次请求1000字节
                request_message = f'FILE {filename} GET START {start} END {end}'

                # 请求并接收数据块（重传机制）
                data_response = send_and_receive(client_socket, request_message, server_ip, transfer_port, timeout=2)

                if data_response is None:
                    print("Failed to receive data block.")
                    client_socket.close()
                    return

                print(f"Received data for {filename} (start: {start}, end: {end})")

                # 解析并解码Base64数据
                base64_data = data_response.split("DATA ")[1].strip()
                binary_data = base64.b64decode(base64_data)

                # 将数据写入文件
                f.seek(start)
                f.write(binary_data)

                received_data += len(binary_data)
                print(f"Progress: {received_data}/{file_size} bytes")

            # 下载完成后，发送CLOSE请求
            close_message = f"FILE {filename} CLOSE"
            close_response = send_and_receive(client_socket, close_message, server_ip, transfer_port, timeout=2)

            if close_response is not None and "CLOSE_OK" in close_response:
                print(f"Download of {filename} complete.")
            else:
                print("Failed to close the file properly.")

    else:
        print(f"Error: {response}")

    client_socket.close()


# 客户端函数，处理多个文件的下载
def udp_client(server_ip, server_port, file_list):
    for filename in file_list:
        print(f"Starting download for {filename}...")
        download_file(server_ip, server_port, filename)


if __name__ == "__main__":
    server_ip = 'localhost'
    server_port = 51234  # 服务器端口
    file_list = ['example.txt', 'another_file.txt', 'sample_file.pdf']  # 要下载的文件列表
    udp_client(server_ip, server_port, file_list)
