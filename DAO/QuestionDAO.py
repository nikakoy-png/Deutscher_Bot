from abc import ABC, abstractmethod


class QuestionDAO(ABC):
    @abstractmethod
    def add(self, obj):
        raise NotImplementedError

    @abstractmethod
    def get(self, question_id):
        raise NotImplementedError
