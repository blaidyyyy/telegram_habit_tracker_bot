import aiogram
import asyncio
import json
#import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from config import TOKEN

bot = Bot(token = TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message : Message):
    await message.answer("Привет! Я твой трекер привычек.\n\n"
        "Доступные команды:\n"
        "/add_habit + название привычки - добавить привычку\n"
        "/list_habits - список привычек\n"
        "/complete + название привычки - отметить выполнение\n"
        "/stats - статистика"
    )

@dp.message(Command("add_habit"))
async def add_habit_command(message : Message):
    habit_name = message.text.replace('/add_habit', '').strip()
    
    if not habit_name:
        await message.answer("Пожалуйста, укажите название привычки после команды:\n/add_habit + название привычки")

    try:
        with open('habits.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        
        data = {"habits": []}
    
    new_habit = {
        "name": habit_name,
        "streak": 0
    }
    data["habits"].append(new_habit)

    with open('habits.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    
    await message.answer(f"Привычка '{habit_name}' добавлена! ✅")

async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    #logging.basicConfig(level = logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
        
