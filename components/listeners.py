

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ListenerInterface:
    """
    base interface defined for listenable objects

    """
    def __init__(self):
        pass

    def update(self, listener):
        """
        function will be called by the BaseListener whenever event occurs
        :return: None
        """
        raise NotImplemented


class BaseListener:
    """
    Base class for Event Listeners
    Specific listeners need to extend this class
    """

    def __init__(self, is_raw_call=True):
        """
        extending classes need to call the init function with is_raw_class as False
        :param is_raw_call: indicate whether called by extending class
        """
        # list of ListenerInterface objects
        self.list_of_listeners = []
        # message to be forwarded to the registered listening classes
        self.update_message = None
        # checks for raw call to the abstract class
        if is_raw_call:
            raise NotImplemented

    def register_listener(self, listenable: ListenerInterface):
        """
        adds listener class to the list of listeners list
        :param listenable: ListenerInterface object to be registered
        :return: None
        """
        assert isinstance(listenable, ListenerInterface)
        self.list_of_listeners.append(listenable)

    def unregister_listener(self, listenable: ListenerInterface):
        """
        removes the listener class from the listeners list
        :param listenable: ListenerInterface object to be removed
        :return: None
        """
        assert isinstance(listenable, ListenerInterface)
        self.list_of_listeners.remove(listenable)

    def update_listeners(self):
        """
        calls the update function of the all registered listeners
        :return: None
        """
        for listener in self.list_of_listeners:
            listener.update(self.update_message)

    def event_update(self, message):
        """
        function called by the subject classes whenever event occurs
        :param message: message describing the event occurred
        :return: None
        """
        self.update_message = message
        self.update_listeners()
        self.update_message = None

    def get_update(self):
        """
        function called by the subscribing class to read the message
        :return: change message
        """
        return self.update_message


class OnCellUpdatedListener(BaseListener, metaclass=Singleton):
    """
    listener fow when cells on the board are updated

    event message format should be
        tuple[int: x_coord, int:y_coord, Coin]
    if the board is to be cleared, x and y coord should be marked -1
    """
    __instance = None

    def __init__(self):
        BaseListener.__init__(self, is_raw_call=False)


class CellUpdateListenerInterface(ListenerInterface):
    """
    any class registering to OnCellUpdatedListener, must extend this class
    and override on_cell_updated function
    """
    def update(self, listener):
        self.on_cell_updated(listener)

    def on_cell_updated(self, listener):
        """
        to be overridden by the registering class
        :param listener: object ref to calling listener
        :return: None
        """
        raise NotImplemented


class OnDiceRolledListener(BaseListener, metaclass=Singleton):
    """
    listener class for dice roll events
    """
    __instance = None

    def __init__(self):
        BaseListener.__init__(self, is_raw_call=False)


class DiceRollListenerInterface(ListenerInterface):
    """
    any class registering to OnCellUpdatedListener, must extend this class
    and override on_dice_rolled function
    """

    def update(self, listener):
        self.on_dice_rolled(listener)

    def on_dice_rolled(self, listener):
        """
        to be overridden by the registering class
        :param listener: object ref to calling listener
        :return: None
        """
        raise NotImplemented


class OnPlayerSwitchedListener(BaseListener, metaclass=Singleton):
    """
    listener class for when players get turns

    event message format should be
        tuple(BasePlayer, bool: new status)
    """
    __instance = None

    def __init__(self):
        BaseListener.__init__(self, is_raw_call=False)


class PlayerSwitchListenerInterface(ListenerInterface):
    """
    any class registering to OnCellUpdatedListener, must extend this class
    and override on_player_turn_switched function
    """

    def update(self, listener):
        self.on_player_turn_switched(listener)

    def on_player_turn_switched(self, listener):
        """
        to be overridden by the registering class
        :param listener: object ref to calling listener
        :return: None
        """
        raise NotImplemented
