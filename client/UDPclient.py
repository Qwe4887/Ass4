import socket
import base64


# 客户端函数
def udp_client(server_ip, server_port, filename):
    # 创建UDP套接字
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 发送下载请求
    message = f'DOWNLOAD {filename}'
    client_socket.sendto(message.encode(), (server_ip, server_port))
    print(f"Sent message: {message}")

    # 接收服务器响应
    try:
        client_socket.settimeout(2)  # 设置超时时间为2秒
        response, server_address = client_socket.recvfrom(1024)
        print(f"Received response: {response.decode()}")

        # 解析服务器的响应
        if response.decode().startswith('OK'):
            # 获取文件大小和传输端口
            parts = response.decode().split()
            file_size = int(parts[3])  # 'SIZE'后面是文件大小
            transfer_port = int(parts[5])  # 'PORT'后面是端口号

            # 创建文件以保存下载的数据
            with open(f"downloaded_{filename}", 'wb') as f:
                received_data = 0
                # 请求并接收数据块
                while received_data < file_size:
                    start = received_data
                    end = min(start + 1000, file_size)  # 每次请求1000字节
                    request_message = f'FILE {filename} GET START {start} END {end}'
                    client_socket.sendto(request_message.encode(), (server_ip, transfer_port))

                    # 等待服务器回应
                    data_response, _ = client_socket.recvfrom(2048)
                    print(f"Received data for {filename} (start: {start}, end: {end})")

                    # 解析并解码Base64数据
                    base64_data = data_response.decode().split("DATA ")[1].strip()
                    binary_data = base64.b64decode(base64_data)

                    # 将数据写入文件
                    f.seek(start)
                    f.write(binary_data)

                    received_data += len(binary_data)
                    print(f"Progress: {received_data}/{file_size} bytes")

                # 下载完成后，发送CLOSE请求
                client_socket.sendto(f"FILE {filename} CLOSE".encode(), (server_ip, transfer_port))
                print(f"Download of {filename} complete.")
        else:
            print(f"Error: {response.decode()}")

    except socket.timeout:
        print("Request timed out.")

    finally:
        client_socket.close()


if __name__ == "__main__":
    server_ip = 'localhost'
    server_port = 51234  # 服务器端口
    filename = 'example.txt'  # 要下载的文件
    udp_client(server_ip, server_port, filename)
