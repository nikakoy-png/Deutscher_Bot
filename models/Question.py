import json


class Question:
    def __init__(self, data):
        print(data)
        self.__question_text: str = data['question']
        self.__answers: list[str] = data['answers']
        self.__correct_answers: str = data['correct_answer']
        self.__explanation: str = data['explanation']
        self.__message_id: None | int = None
        self.users_answers = {}

    def get_question_text(self) -> str:
        return self.__question_text

    def get_answers(self) -> list[str]:
        return self.__answers

    def get_correct_answers(self) -> str:
        return self.__correct_answers

    def get_explanation(self) -> str:
        return self.__explanation

    def get_message_id(self) -> int | None:
        return self.__message_id

    def set_message_id(self, message_id: int) -> None:
        self.__message_id = message_id

    def __repr__(self) -> str:
        return f"""
        __question_text: {self.__question_text}
        __answers: {self.__answers}
        __correct_answer: {self.__correct_answers}
        __explanation: {self.__explanation}"""
