from abc import ABC, abstractmethod


class BaseItem(ABC):
    @abstractmethod
    def to_json(self):
        pass

    @staticmethod
    @abstractmethod
    def from_json(el):
        pass


class DataProcessor(ABC):

    @staticmethod
    @abstractmethod
    def process_item(item):
        pass

    @staticmethod
    @abstractmethod
    def process_items(items):
        pass
