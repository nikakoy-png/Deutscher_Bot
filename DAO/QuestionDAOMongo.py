from pymongo import MongoClient
from DAO.QuestionDAO import QuestionDAO
from models.Question import Question
import certifi
ca = certifi.where()

class QuestionDAOMongo(QuestionDAO):
    def __init__(self):
        # Подключение к MongoDB
        self.client = MongoClient("mongodb+srv://xdnikbel:NaFigTeBeEto@cluster0.tcpke18.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)
        self.db = self.client["main"]
        self.collection = self.db['questions']

    def add(self, obj: Question):
        # Добавление вопроса в коллекцию
        question_data = {
            'question_text': obj.get_question_text(),
            'answers': obj.get_answers(),
            'correct_answers': obj.get_correct_answers(),
            'explanation': obj.get_explanation()
        }
        self.collection.insert_one(question_data)

    def get(self, question_id):
        question_data = self.collection.find_one({'id': question_id})
        if question_data:
            question = Question(
                question_text=question_data['question_text'],
                answers=question_data['answers'],
                correct_answers=question_data['correct_answers'],
                explanation=question_data['explanation']
            )
            return question
        else:
            return None
