# TG/VK Polling Bot

## Overview
This is a simple polling bot for VKontakte (VK) messenger that allows users to participate in quizzes and answer questions.

## Requirements
- Python 3.x
- VK API token
- Redis server

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/vk-polling-bot.git
   cd vk-polling-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp sexample.env .env
   ```
   Edit the `.env` file with your VK API token, TG API token and Redis server details.


4. Run the telegram bot:
   ```bash
   python3 tg_bot.py
   ```
5. Run the vk bot:
   ```bash
   python3 vk_bot.py
   ```

## Usage
- Send "Новый вопрос" to get a new question.
- Send "Сдаться" to give up and see the correct answer.
- Send "Мой счёт" to check your current score.

## Troubleshooting
If you encounter any issues, feel free to open an issue in the GitHub repository.