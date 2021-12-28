import threading
from functools import wraps

TIME_OUT = 10


class Thread(object):

    def __init__(self, loop):
        super(Thread, self).__init__()
        self.fun = loop
        self.loop_proc = None
        self.running = True

    def __call__(self, *args, **kwargs):
        self.loop_proc = threading.Thread(target=self.fun, args=args, kwargs=kwargs) # target：需要开启线程的可调用对象; args：在参数target中传入的可调用对象的参数元组; kwargs：在参数target中传入的可调用对象的关键字参数字典
        self.loop_proc.setDaemon(True) # 将该线程设置为守护线程
        self.loop_proc.start() # 开启线程活动
        return self

    def stop(self):
        self.running = False

    @staticmethod
    def respond(func):
        @wraps(func)
        def make_resp(handle, tid):
            """ 需要注意的是，和装饰的函数参数含义需一致 """
            event = threading.Event() # 创建事件对象，内部标志默认为False
            event.wait(timeout=TIME_OUT) # 阻塞线程直到内部标志为True，或者发生超时事件
            return func(handle, tid)
        return make_resp
