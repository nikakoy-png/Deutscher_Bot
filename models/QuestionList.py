from typing import Any, Generator

from models.Question import Question
from AI import AI


class QuestionList:
    def __init__(self):
        self.__ai: AI = AI()
        self.__questions = self.make_list_questions(self.__ai.get_questions())

    @staticmethod
    def make_list_questions(questions) -> Generator[Question, Any, None]:
        return (Question(item) for item in questions)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self.__questions)
        except StopIteration:
            self.get_questions()
            return next(self.__questions)

    def get_questions(self):
        self.__questions = self.make_list_questions(self.__ai.get_questions())



