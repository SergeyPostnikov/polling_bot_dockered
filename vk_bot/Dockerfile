FROM python:3.8.10

WORKDIR /vk-bot/

COPY requirements.txt /tg-bot/

RUN pip3 install -r requirements.txt
COPY . /vk-bot/

CMD ["python3", "vk_bot.py"]