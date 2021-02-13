import queue
import threading
import pickle


class BaseTransmissionQueue:

    FOR_ALL = "all"
    __singleton = None

    def __init__(self):
        # if only one recipient, assign a Queue object.
        # else make it a dict with remote peer address as key
        self.queue_list = None
        pass

    def __new__(cls, *args, **kwargs):
        if cls.__singleton is None:
            cls.__singleton = object.__new__(cls)
        return cls.__singleton

    def build(self):
        raise NotImplemented

    def push(self, message, recipient_id: str = FOR_ALL):
        """
        pushes in the message to be transmitted to the sub queues
        Input should be a tuple pair of data to be sent and
        :param message: message to be transferred (non-coded string)
        :param recipient_id: recipient of the message
        :return: None
        """
        raise NotImplemented

    def get_message(self, recipient_id: str = None):
        """
        reads the recipient specific queue and gets th message to be transmitted
        :param recipient_id:
        :return:
        """
        raise NotImplemented


class BaseReceptionQueue(threading.Thread):

    __singleton = None

    def __int__(self):
        threading.Thread.__init__(self)
        self._reception_queue = queue.Queue()
        # list of all registered listeners
        self.listeners_register = []
        # buffer to temporarily store the data, for the listeners to read
        self.buffer = None
        # flag to control the mail loop
        self._execution_control_flag = False

    def __new__(cls, *args, **kwargs):
        if cls.__singleton is None:
            cls.__singleton = object.__new__(cls)
        return cls.__singleton

    def build(self):
        pass

    def push(self, decoded_message: str, from_address: str = None):
        """
        Function to push the freshly recieved message from the remote peer
        The function will be accessed by the recipient thread
        The message should be pushed to the queue as a tuple
        :param decoded_message: message received from the remote peer
        :param from_address: ip address of format xxx.xxx.xxx.xxx
        :return: None
        """
        raise NotImplemented

    def _notify_listeners(self):
        for registered_listener in self.listeners_register:
            # call the update function of the listener
            registered_listener.update()

    def run(self) -> None:
        raise NotImplementedError


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
