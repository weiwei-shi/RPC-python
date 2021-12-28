from Task import TaskHandle
from ServerTcp import ServerTcp


class Server(TaskHandle, ServerTcp):
    """
    服务端的主要任务是：
    1. 创建一个指定类对象
    2. 监听网络事件
    3. 解析调用事件，用对象调用函数
    4. 将结果发回网络端
    """

    def __init__(self, cls, *args, **kwargs):
        super(Server, self).__init__()
        self._obj = cls(*args, **kwargs)

    def run(self):
        """ 处理rpc调用 """
        while True:
            self.process()
            while self.has_events:
                event = self.get_next_event()
                host, data = event[1], event[2]
                try:
                    ret = self._process_rpc_task(data)
                    data = '' if ret is None else ret
                    self.send(host, data)
                except Exception as e:
                    # TODO: 把报错信息发回客户端
                    print(e)

    def _process_rpc_task(self, data):
        task = self.unpack_task(data)
        method = getattr(self._obj, task.name, None) # 在特定类cls中找到task.name对应的属性值,即找到函数
        if method:
            value = method(*task.args, **task.kwargs) # 得到函数返回值
            if value:
                rid = self.add_respond(task.tid, value)
                ret = self.pack_respond(rid)
                self.pop_respond(rid)
                return ret
        else:
            raise RuntimeError("{} no not have rpc method {}".format(self._obj.__class__, task.name))
