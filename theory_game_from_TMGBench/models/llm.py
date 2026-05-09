from abc import abstractmethod


class LLM:
    def __init__(self):
        pass

    def __str__(self):
        pass

    @abstractmethod
    def reset(self):
        raise NotImplementedError

    @abstractmethod
    def set_context(self):
        raise NotImplementedError

    @abstractmethod
    def invoke(self):
        raise NotImplementedError