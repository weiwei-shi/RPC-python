import sys
sys.path.append('./')

from Client import Client


class Function(object):

    def upper(self, str):
        pass


class TestRPC():

    @staticmethod
    def start_client():
        c = Client(Function)
        c.connect(host='localhost', port=3200)
        print(c.upper('distribute'))
        c.close()


if __name__ == '__main__':
    t = TestRPC()
    t.start_client()