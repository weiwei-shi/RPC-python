from Server import Server


class Function(object):

    def sum(self, a, b):
        return "%.2f" % (a + b)

    def upper(self, str):
        return str.upper()


s = Server(Function)
s.connect(host='localhost', port=3200)
s.run()
s.close()