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





@dp.message(Command("list_habits"))
async def list_of_habits(message : Message):
    user_id = str(message.from_user.id)
    

    try:
        with open('habits.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

    except FileNotFoundError:
        await message.answer("📝 У вас пока нет привычек! Добавьте первую с помощью /add_habit")
        return

    if user_id not in data.get("users", {}):
        await message.answer("📝 У вас пока нет привычек! Добавьте первую с помощью /add_habit")
        return

    user_habits = data["users"][user_id]["habits"]

    if not user_habits:
        await message.answer("📝 У вас пока нет привычек! Добавьте первую с помощью /add_habit")
        return
    
    habits_list = "📋 Ваши привычки:\n\n"
    for i, habit in enumerate(user_habits, 1):
        habits_list += f"{i}. {habit['name']} - {habit['streak']} дней подряд\n"

    await message.answer(habits_list)



@dp.message(Command("add_habit"))
async def add_habit_command(message : Message):
    habit_name = message.text.replace('/add_habit', '').strip()
    user_id = str(message.from_user.id)
    
    if not habit_name:
        await message.answer("Пожалуйста, укажите название привычки после команды:\n/add_habit + название привычки")
        return

    try:
        with open('habits.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        
        data = {"users": {}}
    
    if user_id not in data["users"]:
        data["users"][user_id] = {"habits": []}
    
    
    for habit in data["users"][user_id]["habits"]:
        if habit["name"].lower() == habit_name.lower():
            await message.answer(f"Привычка '{habit_name}' уже существует!")
            return
    
    
    new_habit = {"name": habit_name, "streak": 0}
    data["users"][user_id]["habits"].append(new_habit)
    
    

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
        
