import sys
sys.path.append('./')

from Client import Client


class Function(object):

    def sum(self, a, b):
        pass


class TestRPC():

    @staticmethod
    def start_client2():
        c = Client(Function)
        c.connect(host='localhost', port=3200)
        print(c.sum(8.8, 4.45))
        c.close()


if __name__ == '__main__':
    t = TestRPC()
    t.start_client2()