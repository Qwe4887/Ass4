import socket
import os

# 定义客户端连接的服务器地址和端口
HOST = 'localhost'
PORT = 51234
DOWNLOAD_PORT = 50001

# 向服务器发送请求并接收响应
def send_request(filename, file_transfer_client_socket):
    print(f"发送请求：下载文件 {filename}")  # 调试信息
    # 发送下载请求
    request = f"DOWNLOAD {filename}"
    client_socket.sendto(request.encode('utf-8'), (HOST, PORT))

    # 接收服务器响应
    response, _ = client_socket.recvfrom(1024)
    response_message = response.decode('utf-8')
    print(f"收到服务器响应: {response_message}")

    # 解析服务器响应
    if response_message.startswith("OK"):
        # 获取文件的大小和文件传输的端口
        file_info = response_message.split()
        file_size = int(file_info[3])
        transfer_port = int(file_info[5])

        bytes_received = 0
        with open(f"received_{filename}", "wb") as file:
            while bytes_received < file_size:
                # 请求下一个字节范围
                start = bytes_received
                end = min(start + 1023, file_size - 1)  # 每次请求1024字节
                request_data = f"FILE {filename} GET START {start} END {end}"
                print(f"发送请求：字节范围 {start}-{end}")  # 调试信息
                file_transfer_client_socket.sendto(request_data.encode('utf-8'), (HOST, transfer_port))

                # 接收服务器返回的数据
                response_data, _ = file_transfer_client_socket.recvfrom(1024)
                response_message = response_data.decode('utf-8')

                # 打印返回的数据块（前20个字符）
                print(f"接收到的数据块：{response_message[:20]}...")

                # 处理返回的数据
                if response_message.startswith(f"FILE {filename} OK"):
                    # 提取数据
                    data = response_message.split("DATA ")[1]
                    file.write(bytes.fromhex(data))
                    bytes_received += len(bytes.fromhex(data))

                    # 打印接收进度
                    print(f"下载进度: {bytes_received}/{file_size} 字节", end="\r")

                else:
                    print("错误: 无法获取文件数据")
                    break

        # 文件下载完毕后发送CLOSE请求
        file_transfer_client_socket.sendto(f"FILE {filename} CLOSE".encode('utf-8'), (HOST, transfer_port))
        print(f"\n文件 {filename} 下载完成！")
    else:
        print("错误：文件不存在或请求失败")

# 主程序
if __name__ == "__main__":
    # 从文件列表中读取文件名并依次下载
    try:
        with open("files.txt", "r") as f:
            filenames = f.readlines()
        print(f"找到文件列表：{filenames}")
    except FileNotFoundError:
        print("错误：files.txt 文件未找到!")
        exit()

    # 创建客户端套接字
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 通过独立的套接字来处理文件传输
    file_transfer_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 逐个请求文件下载
    for filename in filenames:
        filename = filename.strip()  # 去除换行符
        print(f"开始下载文件: {filename}")
        send_request(filename, file_transfer_client_socket)

    # 关闭客户端套接字
    client_socket.close()
    file_transfer_client_socket.close()
