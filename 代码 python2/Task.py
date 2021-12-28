import pickle
import uuid


class Task(object):
    VOID_RETURN = 0 # 不需要返回值
    REQUIRE_CALLBACK = 1 # 需要返回值

    CALL_BACK_KEY = 'callback'

    def __init__(self, fun=None, *args, **kwargs):
        self._id = 0
        self._type = Task.VOID_RETURN
        self._fun_name = fun       # 函数名称，为string类型
        self._fun_args = args      # 函数输入的参数
        self._fun_kwargs = kwargs  # 函数输入的成对键值对
        self._fun_callback = None  # 函数的回调值
        self._extra_callback()
        self._gen_id()

    def _extra_callback(self):
        if Task.CALL_BACK_KEY in self._fun_kwargs \
                and callable(self._fun_kwargs[Task.CALL_BACK_KEY]): # callable：判断是否可调用
            self._type = Task.REQUIRE_CALLBACK
            self._fun_callback = self._fun_kwargs.pop(Task.CALL_BACK_KEY)

    def set_type(self, val):
        """ 调用类型，
        0: 无需要返回值
        1: 需要返回值
        """
        self._type = val

    @property
    def tid(self):
        return self._id

    @property
    def name(self):
        return self._fun_name

    @property
    def args(self):
        return self._fun_args

    @property
    def kwargs(self):
        return self._fun_kwargs

    @property
    def callback(self):
        return self._fun_callback

    def _gen_id(self):
        self._id = uuid.uuid1() # 根据当前的时间戳和MAC地址生成uuid码

    def dumps(self):
        if self._fun_name is None:
            raise RuntimeError('Task must be assigned before serialize!')
        data = {
            'tid': self._id,
            'fun_name': self._fun_name,
            'fun_args': self._fun_args,
            'fun_kwargs': self._fun_kwargs
        }
        if self._type:
            data['type'] = self._type
        return pickle.dumps(data) # 将数据编码为二进制数据

    def loads(self, data):
        fun_info = pickle.loads(data) # 将数据解码
        self._id = fun_info.get('tid')
        self._type = fun_info.get('type', Task.VOID_RETURN)
        self._fun_name = fun_info.get('fun_name')
        self._fun_args = fun_info.get('fun_args')
        self._fun_kwargs = fun_info.get('fun_kwargs')
        return self


class TaskRespond(object):

    def __init__(self, rid=None, value=None):
        self._id = rid
        self._ret_value = value

    @property
    def rid(self):
        return self._id

    @property
    def value(self):
        return self._ret_value # 得到函数返回值

    def dumps(self):
        if self._ret_value is None:
            raise RuntimeError('Respond must be assigned before serialize!')
        data = {
            'tid': self._id,
            'value': self._ret_value,
        }
        return pickle.dumps(data)

    def loads(self, data):
        ret_info = pickle.loads(data)
        self._id = ret_info.get('tid')
        self._ret_value = ret_info.get('value')
        return self


class TaskHandle(object):
    """ 管理task的创建，执行，和销毁 """
    def __init__(self):
        super(TaskHandle, self).__init__()
        self._tasks = dict()
        self._resps = dict()

    def add_task(self, fun, *args, **kwargs):
        task = Task(fun, *args, **kwargs)
        self._tasks[task.tid] = task
        return task.tid

    def pop_task(self, tid):
        return self._tasks.pop(tid, None)

    def add_respond(self, rid, value):
        resp = TaskRespond(rid, value)
        self._resps[resp.rid] = resp
        return resp.rid

    def pop_respond(self, rid):
        resp = self._resps.pop(rid, None)
        if resp:
            return resp.value

    def pack_task(self, tid):
        task = self._tasks.get(tid)
        if task:
            return task.dumps()

    def pack_respond(self, rid):
        respond = self._resps.get(rid)
        if respond:
            return respond.dumps()

    def unpack_task(self, data):
        task = Task().loads(data)
        self._tasks[task.tid] = task
        return task

    def unpack_respond(self, data):
        resp = TaskRespond().loads(data)
        self._resps[resp.rid] = resp
        return resp
