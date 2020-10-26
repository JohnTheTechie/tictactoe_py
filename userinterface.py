
import queue


class CommQueue:

    __CommQueue = None

    def __init__(self):
        self.HMI_Queue = queue.Queue()

    def __new__(cls, *args, **kwargs):
        if cls.__CommQueue is None:
            cls.__CommQueue = object.__new__(cls)
        return cls.__CommQueue

    def get_hmi_queue(self):
        return self.HMI_Queue


class PrintedInterface:

    def __init__(self):
        pass

    def print_game_screen(self):
        print("=====================================")
        print("     Plr_1                  Plr_2    ")
        print("       X                      O      ")
        print("                                     ")
        print("                                     ")
        print("            A     B     C            ")
        print("          ----- ----- -----          ")
        print("         |     |     |     |         ")
        print("       1 |     |     |     |         ")
        print("         |     |     |     |         ")
        print("          ----- ----- -----          ")
        print("         |     |     |     |         ")
        print("       2 |     |     |     |         ")
        print("         |     |     |     |         ")
        print("          ----- ----- -----          ")
        print("         |     |     |     |         ")
        print("       3 |     |     |     |         ")
        print("         |     |     |     |         ")
        print("          ----- ----- -----          ")
        print("                                     ")
        print(" Current Player: Plr_X               ")
        print("                                     ")
        print("                                     ")
        print("                                     ")

