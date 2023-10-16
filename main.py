import os
import re
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from environs import Env


def parse_quiz(foldername='quiz-questions'):
    pattern = r"Вопрос (\d+):(.*?)(Ответ:\s*.*?)(?:\n\n|\Z)"
    quiz = []
    for foldername, subfolders, filenames in os.walk(foldername):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            
            with open(file_path, encoding='koi8-r') as f:
                quiz = f.read()

            matches = re.findall(pattern, quiz, re.DOTALL)
            for match in matches:
                question = match[1].strip()
                answer = match[2].strip()
                quiz.append({'question': question, 'answer': answer})
    return quiz


def echo(update, context):
    update.message.reply_text(update.message.text)


def start(update, context):
    update.message.reply_text("Привет! Я эхобот. Отправьте мне сообщение, и я отправлю его вам обратно.")


if __name__ == '__main__':
    env = Env()
    env.read_env()
    tg_key = env.str('TG_API_KEY')
    updater = Updater(tg_key, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, echo))
    updater.start_polling()
    updater.idle()
