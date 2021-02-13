

class Observer:
    def __init__(self):
        pass

    def update(self):
        raise NotImplemented


class Observable:

    def __init__(self):
        self.observer_list = []

    def register_observer(self, observer: Observer):
        self.observer_list.append(observer)
        return self

    def unregister_observer(self, observer: Observer):
        self.observer_list.remove(observer)
        return self

    def notify_observer(self):
        for observer in self.observer_list:
            observer.update()

    def get_change_data(self):
        raise NotImplemented


class Communication
