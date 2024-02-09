from pymongo import MongoClient
from DAO.RatingDAO import RatingDAO
import certifi
ca = certifi.where()

class RatingDAOMongo(RatingDAO):
    def __init__(self):
        # Подключение к MongoDB
        self.client = MongoClient("mongodb+srv://xdnikbel:NaFigTeBeEto@cluster0.tcpke18.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)
        self.db = self.client["main"]
        self.collection = self.db['ratings']

    def create_table(self): pass

    def add_rating(self, user_id, username, rating):
        # Добавление рейтинга в коллекцию
        rating_data = {
            'user_id': user_id,
            'username': username,
            'rating': rating
        }
        self.collection.replace_one({'user_id': user_id}, rating_data, upsert=True)

    def get_rating(self, user_id):
        # Получение рейтинга из коллекции по user_id
        rating_data = self.collection.find_one({'user_id': user_id})
        if rating_data:
            return rating_data['rating']
        else:
            return None

    def update_rating(self, user_id, new_rating):
        # Обновление рейтинга в коллекции по user_id
        self.collection.update_one({'user_id': user_id}, {'$set': {'rating': new_rating}})

    def get_top_ratings(self, limit=10):
        # Получение топа рейтингов из коллекции
        result = list(self.collection.find().sort('rating', -1).limit(limit))
        print(result)  # Добавим этот вывод для отладки
        return result

    def close_connection(self):
        # Закрытие соединения с MongoDB
        self.client.close()
