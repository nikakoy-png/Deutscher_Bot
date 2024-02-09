import asyncio
import os
import sqlite3
import time
from multiprocessing import Manager
from typing import Any, Dict, List

from aiogram import Bot, Dispatcher, types
from aiogram import Router
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER, Command
from aiogram.types import InlineKeyboardButton, ChatMemberUpdated
from asgiref.sync import async_to_sync
from celery import Celery
from celery.utils.log import get_task_logger
import redis

from DAO.QuestionDAOMongo import QuestionDAOMongo
from DAO.QuestionDAOSQLite import QuestionDAOSQLite
from DAO.RatingDAOMongo import RatingDAOMongo
from DAO.RatingDAOSQLite import RatingDAOSQLite
from models.Question import Question
from models.QuestionList import QuestionList
from dotenv import load_dotenv

load_dotenv()

router = Router()
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()
db_r = RatingDAOSQLite()
db_q = QuestionDAOSQLite()
GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID')
logger = get_task_logger(__name__)
question_list = QuestionList().__iter__()
redis_conn = redis.StrictRedis(host='localhost', port=6379, db=0)

app = Celery('tasks', broker=os.getenv('URL_BROKER'))
app.conf.broker_connection_retry_on_startup = True
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Oslo',
    enable_utc=True,
)

answers_dict = {}


async def main_scenario():
    while True:
        print("Task main_worker_question started")
        answers_dict.clear()
        question = question_list.__next__()
        await send_question(question)
        await asyncio.sleep(30)
        await give_right_answer(question)
        try:
            print(get_answers_dict())
            correct_answers_users = get_answers_dict()[question.get_correct_answers()]
            await upd_user_rating(correct_answers_users)
        except Exception as e:
            print(f"An error occurred in upd_user_rating: {str(e)}")
        finally:
            clear_answers_table(question.get_answers())
        await asyncio.sleep(30)
        print("Task main_worker_question completed")


@app.task(name='send_question')
def main_worker_question():
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main_scenario())
    except Exception as e:
        print(f"An error occurred in main_worker_question: {str(e)}")


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def welcome_new_members(event: ChatMemberUpdated):
    chat_id = event.chat.id

    if chat_id == GROUP_CHAT_ID:
        member = event.new_chat_member
        user_id = member.user.id
        username = member.user.first_name if member.user.first_name else member.user.username

        db_r.add_rating(user_id=user_id, username=username, rating=0)

        await bot.send_message(
            chat_id=chat_id,
            text=f"Herzlich willkommen, {username}! 🇩🇪\n\n"
                 f"In unserer Gruppe finden alle 15 Minuten Deutschkenntnis-Umfragen statt. "
                 f"Sie können auch nur auf Deutsch mit anderen Mitgliedern kommunizieren, um Ihre Sprachkenntnisse zu üben. Viel Spaß und Erfolg beim Lernen! 🌐📚"
        )


from aiogram import types


async def rating(message: types.Message):
    users = db_r.get_top_ratings()

    if users:
        rating_text = "🌟 TOP RANKING:\n"
        for index, (user_id, username, rating) in enumerate(users, start=1):
            rating_text += f"    {index}. {username} - {rating} Punkte\n"

        await bot.send_message(GROUP_CHAT_ID, rating_text)
    else:
        await bot.send_message(GROUP_CHAT_ID, "No ratings available.")


async def send_question(question: Question):
    try:
        logger.info("Sending question sync")
        question_text = question.get_question_text()
        options = question.get_answers()

        if not all(isinstance(option, str) for option in options):
            raise ValueError("Options should be a list of strings.")

        inline_keyboard = [
            [InlineKeyboardButton(text=option, callback_data=option)] for option in options
        ]

        markup = types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        print("Before sending message")
        formatted_message = (
            f"🤔 Frage:\n\n"
            f"{question_text}\n\n"
            f"Wähle deine Antwort und warte auf die Erklärung in 15 Minuten! ⏰"
        )
        await bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=formatted_message,
            reply_markup=markup
        )
        print("After sending message")

    except Exception as e:
        print(f"An error occurred in send_question_sync: {str(e)}")


async def upd_user_rating(users):
    for user_id in users:
        try:
            user_id_int = int(user_id)
            db_r.add_points(user_id_int, points=1)
        except ValueError:
            print(f"Invalid user_id: {user_id}")


async def give_right_answer(question: Question):
    answers = question.get_answers()
    await bot.send_message(
        GROUP_CHAT_ID,
        f"""🌟 Frage:\n{question.get_question_text()} 🤔\n\n"""
        f"""📝 Antworten:\n"""
        f"""{"".join([f"• {ans} 🟣\n" for ans in answers])}\n"""
        # f"""{"".join([f"Antwort: {ans}, {len(answers_dict.get(ans, []))}\n" for ans in answers])}\n"""
        f"""🎯 Richtige Antwort:\n{question.get_correct_answers()} ✅\n"""
        f"""📚 Warum?\n{question.get_explanation()}"""
        f"""\n ❤️ Die nächste Frage kommt in 5 Minuten, viel Glück!"""
    )


@router.callback_query(lambda c: c.data)
async def handle(callback_query: types.CallbackQuery) -> Any:
    global answers_dict
    try:
        choice = callback_query.data
        user_id = callback_query.from_user.id

        for other_choice, users in answers_dict.items():
            if user_id in users:
                answers_dict[other_choice].remove(user_id)
                redis_conn.hdel('answers', other_choice)

        update_answers_dict(choice, user_id)

        inline_keyboard = callback_query.message.reply_markup

        for index, btn in enumerate(inline_keyboard.inline_keyboard):
            inline_keyboard.inline_keyboard[index][-1].text = get_updated_button_text(
                inline_keyboard.inline_keyboard[index][-1].callback_data, user_id)

        await bot.edit_message_text(
            text=callback_query.message.text,
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=inline_keyboard
        )

    except Exception as e:
        print(f"An error occurred in handle: {str(e)}")


def get_updated_button_text(button_text, user_id):
    count = len(answers_dict.get(button_text, []))
    updated_text = f"{button_text} ({count})"
    return updated_text


def get_answers_dict() -> Dict[str, List[int]]:
    data = redis_conn.hgetall('answers')
    answers_dict_ = {key.decode(): list(map(int, value.decode().split(','))) for key, value in data.items()}
    return answers_dict_


def set_answers_dict(answers: Dict[str, List[int]]):
    for choice, user_ids in answers.items():
        user_ids_str = ','.join(map(str, [user_id for user_id in user_ids if isinstance(user_id, int)]))
        redis_conn.hset('answers', choice, user_ids_str)


def clear_answers_table(answers):
    for ans in answers:
        redis_conn.hdel('answers', ans)


def update_answers_dict(choice, user_id):
    if choice not in answers_dict:
        answers_dict[choice] = []
    answers_dict[choice].append(int(user_id))
    redis_conn.hset('answers', choice, user_id)


@router.startup()
async def startup():
    main_worker_question.delay()
