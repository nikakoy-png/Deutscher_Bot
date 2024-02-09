from abc import ABC, abstractmethod


class RatingDAO(ABC):
    @abstractmethod
    def create_table(self): pass

    @abstractmethod
    def add_rating(self, user_id, username, rating): pass

    @abstractmethod
    def get_rating(self, user_id): pass

    @abstractmethod
    def update_rating(self, user_id, new_rating): pass

    @abstractmethod
    def get_top_ratings(self, limit): pass

    @abstractmethod
    def close_connection(self): pass
