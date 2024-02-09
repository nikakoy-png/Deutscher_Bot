import sqlite3

from DAO.RatingDAO import RatingDAO


class RatingDAOSQLite(RatingDAO):
    def __init__(self):
        self.conn = sqlite3.connect("../db.db", check_same_thread=False)
        self.create_table()

    def create_table(self):
        query = '''
                CREATE TABLE IF NOT EXISTS ratings (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    rating INTEGER
                )
                '''
        with self.conn:
            self.conn.execute(query)

    def add_rating(self, user_id, username, rating):
        query = '''
            INSERT OR REPLACE INTO ratings (user_id, username, rating) VALUES (?, ?, ?)
        '''
        with self.conn:
            self.conn.execute(query, (user_id, username, rating))

    def get_rating(self, user_id):
        query = '''
            SELECT rating FROM ratings WHERE user_id = ?
        '''
        with self.conn:
            cursor = self.conn.execute(query, (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    def update_rating(self, user_id, new_rating):
        query = '''
            UPDATE ratings SET rating = ? WHERE user_id = ?
        '''
        with self.conn:
            self.conn.execute(query, (new_rating, user_id))

    def get_top_ratings(self, limit=10):
        query = '''
            SELECT user_id, username, rating FROM ratings ORDER BY rating DESC LIMIT ?
        '''
        with self.conn:
            cursor = self.conn.execute(query, (limit,))
            result = cursor.fetchall()
            print(result)  # Добавим этот вывод для отладки
            return result

    def add_points(self, user_id, points):
        query_select = 'SELECT rating FROM ratings WHERE user_id = ?'
        query_update = 'UPDATE ratings SET rating = ? WHERE user_id = ?'
        with self.conn:
            current_rating = self.conn.execute(query_select, (user_id,)).fetchone()
            if current_rating is not None:
                new_rating = int(current_rating[0]) + points
                self.conn.execute(query_update, (new_rating, user_id))

    def close_connection(self):
        self.conn.close()
