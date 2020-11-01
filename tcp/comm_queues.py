import queue
import threading
import pickle


class TransmissionQueue:

    __singleton = None

    def __init__(self):
        self.queue_map = {}

    def __new__(cls, *args, **kwargs):
        if cls.__singleton is None:
            cls.__singleton = object.__new__(cls)
        return cls.__singleton

    def add_a_client(self, client_address):
        if client_address not in self.queue_map:
            self.queue_map[client_address] = queue.Queue()
        else:
            pass

    def get_queue(self, client_address):
        if client_address in self.queue_map:
            return self.queue_map[client_address]
        else:
            raise Exception("queue not configured")

    def push_message(self, message):
        que: queue.Queue
        for client, que in self.queue_map.items():
            que.put(message)


class ReceptionQueue:

    __singleton = None

    def __init__(self):
        self.lock = threading.Lock()
        self.queue = queue.Queue()

    def __new__(cls, *args, **kwargs):
        if cls.__singleton is None:
            cls.__singleton = object.__new__(cls)
        return cls.__singleton

    def push_message(self, message):
        self.lock.acquire()
        self.queue.put(message)
        self.lock.release()

    def get_message(self):
        return self.queue.get()


class Message:

    def __init__(self, pickle_dump = None):
        if pickle_dump is None:
            self.data1 = None
            self.data2 = None
            self.dump = None
        else:
            self.__unpickle_dump(pickle_dump)

    def pickle_it(self):
        return pickle.dumps(self)

    def __unpickle_dump(self, dump):
        temp = pickle.loads(dump)
        assert isinstance(temp, Message)
        self.data1 = temp.data1
        self.data2 = temp.data2
        self.dump = temp.dump
