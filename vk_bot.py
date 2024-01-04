import logging
import time
import vk_api

from db import get_random_question
from environs import Env
from redis import Redis
from redis.exceptions import RedisError
from vk_api.exceptions import VkApiError
from vk_api.keyboard import VkKeyboard
from vk_api.keyboard import VkKeyboardColor
from vk_api.longpoll import VkEventType
from vk_api.longpoll import VkLongPoll
from vk_api.utils import get_random_id


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__file__)


def check_answer(event, vk, db):
    user_id = event.user_id
    answer = event.text.capitalize()    
    right_answer = db.get(f'{user_id}')

    if not right_answer:
        start(event, vk, db)
    
    elif answer == right_answer.decode():
        score_key = f'{user_id}-score'
        current_score = int(db.get(score_key) or 0)
        current_score += 1
        db.set(score_key, current_score)

        db.set(f'{user_id}', '')
        vk.messages.send(
            peer_id=user_id,
            random_id=get_random_id(),
            keyboard=get_menu_keyboard(),
            message='Правильно!'
        )
    else:
        vk.messages.send(
            peer_id=user_id,
            random_id=get_random_id(),
            keyboard=get_menu_keyboard(),
            message='Не правильно!'
        )


def start(event, vk, db):
    user_id = event.user_id
    score_key = f'{user_id}-score'
    db.set(score_key, 0)
    db.set(f'{user_id}', '') 

    vk.messages.send(
        peer_id=user_id,
        random_id=get_random_id(),
        keyboard=get_menu_keyboard(),
        message="Привет! Это бот викторина.\n Чтобы проверить свои силы, нажми - \"Новый вопрос\""
    )


def get_menu_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.SECONDARY)

    return keyboard.get_keyboard()


def new_question(event, vk, db):
    user_id = event.user_id    
    question, answer = get_random_question().values()
    db.set(f'{user_id}', answer)
    vk.messages.send(
        peer_id=user_id,
        random_id=get_random_id(),
        keyboard=get_menu_keyboard(),
        message=question
    )


def give_up(event, vk, db):
    user_id = event.user_id
    answer = db.get(f'{user_id}')
    if answer:
        vk.messages.send(
            peer_id=user_id,
            random_id=get_random_id(),
            keyboard=get_menu_keyboard(),
            message=answer.decode()
        )
        db.set(f'{user_id}', '')
    else:
        start(event, vk, db)


def get_score(event, vk, db):
    user_id = event.user_id
    score_key = f'{user_id}-score'
    vk.messages.send(
        peer_id=user_id,
        random_id=get_random_id(),
        keyboard=get_menu_keyboard(),
        message=int(db.get(score_key) or 0)
    )


def main():
    env = Env()
    env.read_env()
    VK_TOKEN = env.str("VK_TOKEN")

    logger.setLevel(logging.DEBUG)
    logger.info('vk polling bot started')

    try:
        redis_db = Redis(
            host=env.str('REDIS_HOST'),
            port=env.str('REDIS_PORT'),
            # password=env.str('REDIS_PSW'),
            db=0
        )
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        vk = vk_session.get_api()
        longpoll = VkLongPoll(vk_session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'новый вопрос':
                    new_question(event, vk, redis_db)
                elif event.text.lower() == 'сдаться':
                    give_up(event, vk, redis_db)
                elif event.text.lower() == 'мой счёт':
                    get_score(event, vk, redis_db)
                else:
                    check_answer(event, vk, redis_db)
    except VkApiError as err:
        logger.error(f"Vk api error: {err}")
    except RedisError as err:
        logger.error(f"Redis error : {err}")
    except ConnectionError as err:
        logger.exception(err)
        time.sleep(30)
    except Exception as exc:
        logger.error(f"VkBot error: {exc}")
  

if __name__ == '__main__':
    main()
