import RpcServer


def sum(a, b):
    res = "%.2f" % (a + b)
    return res


def upper(str):
    return str.upper()


server = RpcServer.RpcServer()
server.register_function(sum) # 注册方法
server.register_function(upper) # 注册方法
server.loop(5000) # 传入要监听的端口