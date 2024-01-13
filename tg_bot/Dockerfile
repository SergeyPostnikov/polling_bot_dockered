FROM python:3.8.10

WORKDIR /tg-bot/

COPY requirements.txt /tg-bot/

RUN pip3 install -r requirements.txt
COPY . /tg-bot/

CMD ["python3", "tg_bot.py"]