import logging as l

class Stateful:
    def __init__(self):
        self.log = []

    def _set_state(self, state: str, ok: bool = True):
        """
        Stores and logs the current state

        :param state: a string with the state
        :param ok: True if it's a good state, False if it's an error
        :return: no return
        """
        self.ok = ok
        self.state = state
        self.log.append(state)
        if ok:
            l.info("OctoReader: " + state)
        else:
            l.warning("OctoReader: " + state)