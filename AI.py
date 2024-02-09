import json
import logging
import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


class AI:
    def __init__(self, prompt: str = None, model: str = None):
        self.__model = "gpt-3.5-turbo" if not model else model
        self.__prompt = (
            """Generate a German language assignment for B1 level. Create a question based on the Schritte Buch with 
            4 possible answers in JSON format. Ensure each question is unique, marked with the correct answer, 
            and focuses on grammar. Design the questions to be diverse, interesting, and suitable for a Telegram chat. 
            Include an explanation with an example. The JSON format should be { 'questions': 
            [ {'question': text, 'answers': ['answer1', 'answer2', 'answer3', 'answer4'], 
            'correct_answer': 'correct_answer', 'explanation': text}]}"""
            if not prompt else prompt
        )
        self.__client = OpenAI(api_key=OPENAI_API_KEY)

    def get_questions(self):
        response = self.__client.chat.completions.create(
            model=self.__model,
            messages=[
                {"role": "user", "content": self.__prompt},
            ],
            temperature=0.2
        )

        print(json.loads(response.choices[0].message.content)["questions"])
        logging.log(msg=json.loads(response.choices[0].message.content)["questions"], level=logging.INFO)
        return json.loads(response.choices[0].message.content)["questions"]