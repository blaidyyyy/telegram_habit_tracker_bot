import aiogram
import asyncio
import json
#import logging
import aioschedule as schedule
from datetime import datetime

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
        
    )

async def message_to_user(user_id):
    await bot.send_message(user_id, "Не забудьте про свои привычки!")

schedule.every().day.at("10:00").do(message_to_user)



@dp.message(Command("list_habits"))
async def list_of_habits(message : Message):
    user_id = str(message.from_user.id)
    

    
    with open('habits.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    if user_id not in data.get("users", {}):
        await message.answer("📝 У вас пока нет привычек! Добавьте первую с помощью /add_habit")
        return

    user_habits = data["users"][user_id]["habits"]

    
    habits_list = "📋 Ваши привычки:\n\n"
    for i, habit in enumerate(user_habits, 1):
        habits_list += f"{i}. {habit['name']} - {habit['streak']} дней подряд\n"

    await message.answer(habits_list)



@dp.message(Command("add_habit"))
async def add_habit_command(message : Message):
    habit_name = message.text.replace('/add_habit', '').strip()
    user_id = str(message.from_user.id)
    
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


@dp.message(Command("complete"))
async def complete_habit(message : Message):
    user_id = str(message.from_user.id)
    habit_name = message.text.replace('/complete', '').strip()
    
    with open('habits.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

    habit_found = False        
    for habit in data["users"][user_id]["habits"]:

        if habit["name"].lower() == habit_name.lower():
            habit_found = True
            habit["streak"] += 1

            with open('habits.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            
            await message.answer("Так держать!")
            break
            

            
    
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    #logging.basicConfig(level = logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
        
