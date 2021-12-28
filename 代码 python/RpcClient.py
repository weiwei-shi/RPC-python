import socket
import json


# 网络传输协议TCP（使用socket）
class TcpClient(object):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        '''链接Server端'''
        self.socket.connect((host, port))

    def send(self, data):
        '''将数据发送到Server端'''
        self.socket.sendall(data)

    def recv(self, length):
        '''接受Server端回传的数据'''
        return self.socket.recv(length)

    def close(self):
        '''关闭连接'''
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                print(e)
            self.socket = None

# 客户端存根
class ClientStub(object):
    def __getattr__(self, function):
        def _func(*args, **kwargs):
            d = {'method_name': function, 'method_args': args, 'method_kwargs': kwargs}
            self.send(json.dumps(d).encode('utf-8'))  # 发送编码过的数据
            msg = self.recv(1024)  # 接收方法执行后返回的结果
            data = json.loads(msg.decode('utf-8'))
            return data

        setattr(self, function, _func)
        return _func


class RpcClient(TcpClient, ClientStub):
    pass
