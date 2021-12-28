from Task import TaskHandle
from ClientTcp import ClientTcp
from Thread import Thread


class Client(TaskHandle, ClientTcp):
    """
    客户端的主要任务是：
    1. 将类中的非私有函数 提取出来作为rpc函数
    2. 当有函数调用事件时，就创建一个task并发送给对应的服务端
    """

    def __init__(self, cls):
        super(Client, self).__init__()
        self._cls_name = cls.__name__
        self._cls_func = None
        self._methods = self._contain_methods(cls)
        self._proc_thread = None

    def connect(self, host='localhost', port=3154):
        super(Client, self).connect(host, port)
        if self._proc_thread:
            self._proc_thread.stop()
            self._proc_thread = None
        self._proc_thread = Client.process(self)

    def _contain_methods(self, cls):
        if isinstance(cls, dict): # 判断cls的类型是不是dict（字典）
            return cls
        client_methods = set(k for k in dir(self) if not k.startswith('_')) # 将self的方法集中不以“_”开头的存入元素集
        return dict((k, getattr(cls, k)) for k in dir(cls) # 在cls的方法集中如果方法不以“_”开头并且不在上面的元素集中，就将该方法以及它对应的属性值存入字典中
                    if callable(getattr(cls, k)) and not k.startswith('_') and k not in client_methods)

    @Thread
    def process(self):
        super(Client, self).process()
        _events = []
        while self.has_events:
            event = self.get_next_event()
            data = event[1]
            _events.append(self.unpack_respond(data)) # Task文件中
        return _events

    def __getattr__(self, func):
        if func in self._methods:
            # 返回一个东西收集参数
            self._cls_func = func
            return self
        else:
            return object.__getattribute__(self, func)

    def __call__(self, *args, **kwargs):
        if self._cls_func is None:
            raise RuntimeError('no rpc method is initialized')
        if self._cls_func:
            tid = self.add_task(self._cls_func, *args, **kwargs)
            self._last_called = None
            self.send(self.pack_task(tid))
            return self._handle_response(tid)
        else:
            raise RuntimeError('{} is not considered to be a rpc method'.format(self._last_called))

    @Thread.respond
    def _handle_response(self, tid):
        """ 处理有返回值的情况
        会阻塞线程直至收到返回值
        """
        return self.pop_respond(tid) # 得到返回值

    def close(self):
        self._proc_thread.stop()
        self._proc_thread = None
        super(Client, self).close()
