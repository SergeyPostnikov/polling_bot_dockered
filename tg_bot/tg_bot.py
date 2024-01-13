import logging
import time

from db import get_random_question
from environs import Env
from functools import partial
from redis import Redis
from redis.exceptions import RedisError
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__file__)


def check_answer(update, context, db):
    user_id = update.message.from_user.id
    answer = update.message.text.capitalize()
    
    right_answer = db.get(f'{user_id}')
    if not right_answer:
        start(update, context)
    elif answer == right_answer.decode():
        score_key = f'{user_id}-score'
        current_score = int(db.get(score_key) or 0)
        current_score += 1
        db.set(score_key, current_score)

        db.set(f'{user_id}', '')
        update.message.reply_text(
            text='Правильно!',
            reply_markup=get_menu_keyboard()
        )
    else:
        update.message.reply_text(
            text='Не правильно!',
            reply_markup=get_menu_keyboard()
        )


def start(update, context, db):
    user_id = update.message.from_user.id
    score_key = f'{user_id}-score'
    db.set(score_key, 0)

    db.set(f'{user_id}', '') 

    update.message.reply_text(
        "Привет! Это бот викторина.\n Чтобы проверить свои силы, нажми - \"Новый вопрос\"",
        reply_markup=get_menu_keyboard()
    )


def get_menu_keyboard():
    keyboard = [
        [
            KeyboardButton("Новый вопрос"),
            KeyboardButton("Сдаться"),
        ],
        [KeyboardButton("Мой счёт")],
    ]
    return ReplyKeyboardMarkup(keyboard)


def new_question(update, context, db):
    user_id = update.message.from_user.id    
    question, answer = get_random_question().values()
    db.set(f'{user_id}', answer)
    update.message.reply_text(
        text=question,
        reply_markup=get_menu_keyboard()
    )


def give_up(update, context, db):
    user_id = update.message.from_user.id
    answer = db.get(f'{user_id}')
    if answer:
        update.message.reply_text(
            text=answer.decode(), 
            reply_markup=get_menu_keyboard()
        )
        db.set(f'{user_id}', '')
    else:
        start(update, context, db)


def get_score(update, context, db):
    user_id = update.message.from_user.id
    score_key = f'{user_id}-score'
    update.message.reply_text(
        text=int(db.get(score_key) or 0), 
        reply_markup=get_menu_keyboard()
    )


def main():
    env = Env()
    env.read_env()
    tg_key = env.str('TG_API_KEY')

    try:
        redis_db = Redis(
            host=env.str('REDIS_HOST'),
            port=env.str('REDIS_PORT'),
            # password=env.str('REDIS_PSW'),
            db=0
        )

        updater = Updater(tg_key, use_context=True)
        dp = updater.dispatcher
        dp.add_handler(
            CommandHandler(
                "start", 
                partial(start, db=redis_db)
            )
        )

        new_question_handler = MessageHandler(
            Filters.regex(r'^Новый вопрос$'), 
            partial(new_question, db=redis_db)
        )
        dp.add_handler(new_question_handler)

        give_up_handler = MessageHandler(
            Filters.regex(r'^Сдаться$'), 
            partial(give_up, db=redis_db)
        )
        dp.add_handler(give_up_handler)

        get_score_handler = MessageHandler(
            Filters.regex(r'^Мой счёт$'), 
            partial(get_score, db=redis_db)
        )
        dp.add_handler(get_score_handler)    
        
        check_answer_handler = MessageHandler(
            ~Filters.regex(r'^Новый вопрос$|^Сдаться$|^Мой счёт$'),
            partial(check_answer, db=redis_db)
        )
        dp.add_handler(check_answer_handler)

        updater.start_polling()
        updater.idle()
    except RedisError as err:
        logger.error(f"Redis error : {err}")
    except ConnectionError as err:
        logger.exception(err)
        time.sleep(30)
    except Exception as exc:
        logger.error(f"VkBot error: {exc}")



if __name__ == '__main__':
    main()
