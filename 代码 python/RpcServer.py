import socket
import json


# 网络传输协议TCP（使用socket）
class TcpServer(object):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def bind_listen(self, port):
        self.socket.bind(('0.0.0.0', port))
        self.socket.listen(5)

    def accept_receive_close(self):
        '''获取Client端信息并回传，关闭连接'''
        (connect, address) = self.socket.accept()
        msg = connect.recv(1024)
        data = self.on_msg(msg)
        connect.sendall(data) # 回传
        connect.close()


# 序列化和反序列化
class JsonRpc(object):
    def __init__(self):
        self.data = None

    def from_data(self, data):
        '''解析数据'''
        self.data = json.loads(data.decode('utf-8'))

    def call_method(self, data):
        '''解析数据，调用对应的方法变将该方法执行结果返回'''
        self.from_data(data)
        method_name = self.data['method_name']
        method_args = self.data['method_args']
        method_kwargs = self.data['method_kwargs']
        res = self.funs[method_name](*method_args, **method_kwargs)
        data = res
        return json.dumps(data).encode('utf-8')


# 服务端存根
class ServerStub(object):
    def __init__(self):
        self.funs = {}

    def register_function(self, function, name=None):
        '''Server端方法注册，Client端只可调用被注册的方法'''
        if name is None:
            name = function.__name__
        self.funs[name] = function


class RpcServer(TcpServer, JsonRpc, ServerStub):
    def __init__(self):
        TcpServer.__init__(self)
        JsonRpc.__init__(self)
        ServerStub.__init__(self)

    def loop(self, port):
        # 循环监听 5000 端口
        self.bind_listen(port)
        print('Server listen 5000 ...')
        while True:
            self.accept_receive_close()

    def on_msg(self, data):
        return self.call_method(data)