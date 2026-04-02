import abc


class InitCPP:
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def matrix(self):
        pass

    @abc.abstractmethod
    def find_initial_solution(self):
        pass

