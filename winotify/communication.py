import atexit
import threading
import typing
from multiprocessing.connection import Listener as MPL, Client
__all__ = ['Listener', 'Sender']


class Listener:
    def __init__(self):
        self.server = MPL(('localhost', 6060), authkey=b'key')
        self.thread = threading.Thread(name=self.__repr__(), target=self._loop, daemon=True)
        self.callbacks = {}

        atexit.register(self._cleanup)

    def _loop(self):
        while True:
            con = self.server.accept()
            msg = con.recv()
            print(msg)
            con.close()
            self.run_callback(self.callbacks.get(msg, lambda: print('no such callbacks')))

    def run_callback(self, func: typing.Callable):
        """
        call function callback, this method can be overridden
        :param func: callback's function object
        :return:
        """
        return func()

    def start(self):
        self.thread.start()

    def _cleanup(self):
        self.server.close()


class Sender:
    def __init__(self):
        self.con = Client(('localhost', 6060), authkey=b'key')

    def send(self, data):
        self.con.send(data)
        self.con.close()

