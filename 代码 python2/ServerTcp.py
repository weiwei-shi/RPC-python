import socket
import select
import errno
import struct
import logging

logger = logging.getLogger(__name__)


class ServerTcp(object):
    MAX_HOST_CLIENTS_INDEX = 0xfffe # 客户端最大的序号
    NET_CONNECTION_DATA = 2  # data coming
    NET_HEAD_LENGTH_SIZE = 4  # 4 bytes little endian (x86)
    NET_HEAD_LENGTH_FORMAT = '<I'

    def __init__(self):
        super(ServerTcp, self).__init__() # 找到父类
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 定义基于TCP的socket
        self.event = list() # 定义事件列表
        self.conns = dict() # 定义连接字典
        self.inputs = [self.socket]
        self.outputs = list()

    def connect(self, host='localhost', port=5050):
        self.socket.bind((host, port)) # 关联 socket 到指定的网络接口（IP 地址）和端口号
        self.socket.listen(self.MAX_HOST_CLIENTS_INDEX)
        self.socket.setblocking(True) # 将socket连接设为阻塞状态

    def set_blocking(self, is_block):
        self.socket.setblocking(is_block) # 设置阻塞状态

    def send(self, conn_id, data):
        conn = self.conns.get(conn_id)
        if conn:
            head = struct.pack(self.NET_HEAD_LENGTH_FORMAT, len(data))  # 设置数据长度为头数据
            try:
                conn.send(head + data)  # 将数据的长度信息和数据本身一起发送出去
            except socket.error as e:
                logger.info('{}, conn_id: {} sending data failed'.format(e, conn_id))
                conn.close()
        else:
            logger.info('conn_id: {} not found'.format(conn_id))

    def close(self):
        for conn_id, conn in self.conns.items():
            conn.close()
        self.socket.close()

    def process(self):
        readable, writable, exceptional = select.select(self.inputs, self.outputs, self.conns.values()) # 1、select函数阻塞进程，直到inputs中的套接字被触发（即套接字接收到客户端发来的握手信号，从而变得可读），rs返回被触发的套接字（服务器套接字）；
        for conn in readable:                                                                           # 5、select再次阻塞进程，同时监听服务器套接字和获得的客户端套接字；
            if conn is self.socket: # 2、如果是服务器套接字被触发（监听到有客户端连接服务器）
                self._handle_accept_()
            else:                   # 3、当客户端发送数据时，客户端套接字被触发，rs返回客户端套接字，然后进行下一步处理。
                self._handle_recv_(conn)
        for conn in writable:
            pass
        for conn in exceptional:    # 4、处理异常情况
            self._handle_leave_(conn)

    def _handle_accept_(self):
        try:
            conn, addr = self.socket.accept() # 接受客户端的连接请求，返回表示当前连接的conn和客户端地址
            conn.setblocking(False) # 让socket进入非阻塞模式
            self.inputs.append(conn) # inputs加入客户端套接字
            print(conn, addr) # 打印连接信息
            self.conns[id(conn)] = conn # 给conn定义唯一标识符并添加进conns字典
        except Exception as e:
            print(e)
            pass

    def _handle_recv_(self, conn):
        res = bytes()
        while True:
            data = None
            try:
                data = conn.recv(1024)
                if not data:         # 如果收到的数据为空，应将socket断开
                    self._handle_leave_(conn)
                    return -1
            except socket.error as e:
                if e.errno not in (errno.EINPROGRESS, errno.EALREADY, errno.EWOULDBLOCK): # errno.EINPROGRESS:操作正在运行
                    self._handle_leave_(conn)                                                          # errno.EALREADY：操作准备就绪
                    return -1                                                             # errno.EWOULDBLOCK：非阻塞，不需要重新读或写
            if not data:
                break
            res = self._pack_events_(res + data, id(conn)) # 将未处理的数据进行缓存

    def _pack_events_(self, data, conn_id):
        # 将数据提取成一个个事件，进行封装
        recv_len = len(data)
        curr_len = 0
        while True:
            if recv_len - curr_len < self.NET_HEAD_LENGTH_SIZE:
                return data[curr_len:]
            # 此时recv_len - curr_len > self.NET_HEAD_LENGTH_SIZE，需要截取接收到的数据
            data_len = struct.unpack(self.NET_HEAD_LENGTH_FORMAT, data[curr_len: curr_len + self.NET_HEAD_LENGTH_SIZE])[0]
            if recv_len < curr_len + data_len + self.NET_HEAD_LENGTH_SIZE:
                return data[curr_len:]
            # 此时recv_len > curr_len + data_len + self.NET_HEAD_LENGTH_SIZE，需要截取接收到的数据
            curr_len += self.NET_HEAD_LENGTH_SIZE
            self.event.append((self.NET_CONNECTION_DATA, conn_id, data[curr_len: curr_len + data_len]))
            curr_len += data_len

    def _handle_leave_(self, conn):
        conn_id = id(conn)
        if conn_id in self.conns:
            conn = self.conns.pop(conn_id)
            try:
                print('leave {}'.format(conn.getpeername())) # 打印离开信息
                conn.close()
            except Exception as e:
                print(e)
        self.inputs.remove(conn)

    @property
    def has_events(self):
        if self.event:
            return True
        else:
            return False

    def get_next_event(self):
        return self.event.pop(0)
