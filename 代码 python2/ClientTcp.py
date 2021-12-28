import socket
import errno
import struct
import logging

logger = logging.getLogger(__name__)


class ClientTcp(object):
    NET_HEAD_LENGTH_SIZE = 4 # 存放数据长度信息的头部大小
    NET_HEAD_LENGTH_FORMAT = '<I' # 网络数据长度信息的格式
    NET_CONNECTION_DATA = 1 # data coming

    def __init__(self):
        super(ClientTcp, self).__init__() # 找到父类并执行相应方法
        self.socket = None # 定义基于TCP的socket
        self.event = list() # 定义事件列表
        self._buffer = bytes() # 定义缓存数据

    def connect(self, host='localhost', port=5050):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 创建socket对象
        self.socket.connect((host, port)) # 连接服务端
        self.socket.setblocking(True) # 将socket连接设为阻塞状态

    def set_blocking(self, is_block):
        self.socket.setblocking(is_block) # 设置阻塞状态

    def send(self, data):
        head = struct.pack(self.NET_HEAD_LENGTH_FORMAT, len(data)) # 设置数据长度为头数据
        self.socket.send(head + data) # 将数据的长度信息和数据本身一起发送出去

    def process(self):
        # 每次从socket取到数据，应重新进行调用继续接收数据
        self._handle_recv_()

    def _handle_recv_(self):
        data = None
        try:
            data = self.socket.recv(1024)
            if not data:         # 如果收到的数据为空，应将socket断开
                self.close()
                return -1
        except socket.error as e:
            if e.errno not in (errno.EINPROGRESS, errno.EALREADY, errno.EWOULDBLOCK): # errno.EINPROGRESS:操作正在运行
                self.close()                                                          # errno.EALREADY：操作准备就绪
                return -1                                                             # errno.EWOULDBLOCK：非阻塞，不需要重新读或写
        self._buffer = self._pack_events_(self._buffer + data) # 将缓存的数据和接收到的数据重新存入缓存中

    def _pack_events_(self, data):
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
            self.event.append((self.NET_CONNECTION_DATA, data[curr_len: curr_len + data_len]))
            curr_len += data_len

    @property
    def has_events(self):
        if self.event:
            return True
        else:
            return False

    def get_next_event(self):
        return self.event.pop(0)

    def close(self):
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                print(e)
            self.socket = None