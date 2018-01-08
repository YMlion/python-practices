import socket
import threading
import time
import base64
import hashlib


def parse_data(data):
    payload_len = data[1] & 127
    if payload_len == 126:
        extend_payload_len = data[2:4]
        mask = data[4:8]
        decoded = data[8:]
    elif payload_len == 127:
        extend_payload_len = data[2:10]
        mask = data[10:14]
        decoded = data[14:]
    else:
        extend_payload_len = None
        mask = data[2:6]
        decoded = data[6:]

    bytes_list = bytearray()
    for i in range(len(decoded)):
        chunk = decoded[i] ^ mask[i % 4]
        bytes_list.append(chunk)
    body = str(bytes_list, encoding='utf-8')

    return body


def send_msg(conn, msg_bytes):
    """
    WebSocket服务端向客户端发送消息
    :param conn: 客户端连接到服务器端的socket对象,即： conn,address = socket.accept()
    :param msg_bytes: 向客户端发送的字节
    :return:
    """
    import struct

    token = b"\x81"
    length = len(msg_bytes)
    if length < 126:
        token += struct.pack("B", length)
    elif length <= 0xFFFF:
        token += struct.pack("!BH", 126, length)
    else:
        token += struct.pack("!BQ", 127, length)

    msg = token + msg_bytes
    conn.send(msg)
    return True


def handle_msg(sock, addr):
    """ 处理消息 """

    while True:
        try:
            data = sock.recv(4096)
        except Exception as e:
            data = None
        if not data:
            break
        print(parse_data(data))
        send_msg(sock, b'12121')
    sock.close()

    print('Connection from %s:%s closed.' % addr)


def create_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # loacl host ip
    s.bind(('10.32.8.172', 8002))
    s.listen(5)
    print('Waiting for connection...')
    return s


def parse_headers(data):
    """ 解析头部并格式化为字典 """

    header_dict = {}
    data = str(data, encoding='utf-8')

    header, body = data.split('\r\n\r\n', 1)
    header_list = header.split('\r\n')

    first_line = True
    for line in header_list:
        if first_line:
            request_line = line.split(' ')
            if len(request_line) == 3:
                header_dict['method'], header_dict['url'], header_dict['protocol'] = request_line
            first_line = False
        else:
            k, v = line.split(':', 1)
            header_dict[k] = v.strip()

    return header_dict


def getResponseHeader(headers):
    """ 设置响应头部 """

    response_tpl = "HTTP/1.1 101 Switching Protocols\r\n" \
                   "Upgrade:websocket\r\n" \
                   "Connection:Upgrade\r\n" \
                   "Sec-WebSocket-Accept:%s\r\n" \
                   "WebSocket-Location:ws://%s%s\r\n\r\n"

    value = headers['Sec-WebSocket-Key'] + \
        '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    ac = base64.b64encode(hashlib.sha1(value.encode('utf-8')).digest())
    response_str = response_tpl % (
        ac.decode('utf-8'), headers['Host'], headers['url'])
    return response_str


def main():
    """ main方法"""

    s = create_socket()
    while True:
        sock, addr = s.accept()
        data = sock.recv(1024)
        headers = parse_headers(data)
        print(headers)
        sock.send(bytes(getResponseHeader(headers), encoding='utf-8'))

        handle_loop = threading.Thread(target=handle_msg, args=(sock, addr))
        handle_loop.start()


if __name__ == '__main__':
    main()
