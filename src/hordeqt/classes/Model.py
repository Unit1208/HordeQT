class Model:
    performance: float
    queued: int
    jobs: int
    eta: float
    type: str
    name: str
    count: int
    details: dict

    def get(self, name, default=None):
        if hasattr(self, name):
            return self.__getattribute__(name)
        elif default != None:
            return default
        raise KeyError(self, name)