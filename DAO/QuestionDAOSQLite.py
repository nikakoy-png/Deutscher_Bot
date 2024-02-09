import sqlite3

from DAO.QuestionDAO import QuestionDAO
from models.Question import Question


class QuestionDAOSQLite(QuestionDAO):
    def __init__(self):
        self.conn = sqlite3.connect("../db.db", check_same_thread=False)
        self.create_table()

    def create_table(self):
        query = '''
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_text TEXT,
                    answers TEXT,
                    correct_answers TEXT,
                    explanation TEXT
                )
                '''
        with self.conn:
            self.conn.execute(query)

    def add(self, obj: Question):
        query = '''
            INSERT INTO questions (question_text, answers, correct_answers, explanation)
            VALUES (?, ?, ?, ?)
        '''
        answers_str = ",".join(obj.get_answers())
        with self.conn:
            self.conn.execute(query, (obj.get_question_text(), answers_str,
                                      obj.get_correct_answers(), obj.get_explanation()))

    def get(self, question_id):
        pass