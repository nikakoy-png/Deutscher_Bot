import redis
from aiogram import types
from DAO.RatingDAOSQLite import RatingDAOSQLite
from typing import Dict, List

# ... (остальной код)

# Инициализация подключения к Redis
redis_conn = redis.StrictRedis(host='localhost', port=6379, db=0)

# Замена RatingDAOSQLite на RatingDAORedis
class RatingDAORedis:
    def __init__(self):
        pass  # Может потребоваться добавить параметры для подключения к Redis

    def add_rating(self, user_id, username, rating):
        redis_conn.hset('ratings', user_id, rating)

    def add_points(self, user_id, points):
        current_rating = redis_conn.hget('ratings', user_id)
        if current_rating is not None:
            new_rating = int(current_rating) + points
            redis_conn.hset('ratings', user_id, new_rating)
