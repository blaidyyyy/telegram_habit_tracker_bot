import aiogram
import asyncio
import json
import datetime


from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from config import TOKEN

bot = Bot(token = TOKEN)
dp = Dispatcher()

ALL_CHATS_ID = []

@dp.message(CommandStart())
async def cmd_start(message : Message):

    user_id = message.chat.id

    if user_id not in ALL_CHATS_ID:
        ALL_CHATS_ID.append(user_id)

    await message.answer("Привет! Я твой трекер привычек.\n\n"
        "Доступные команды:\n"
        "/add_habit + название привычки - добавить привычку\n"
        "/list_habits - список привычек\n"
        "/complete + название привычки - отметить выполнение\n"

        
        
    )






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
    if not habit_found:
        user_habits = [habit["name"] for habit in data["users"][user_id]["habits"]]
        habits_list = "\n".join([f"• {habit}" for habit in user_habits])
        
        await message.answer(f"❌ Привычка '{habit_name}' не найдена!\n\n"
                           f"📋 Ваши привычки:\n{habits_list}\n\n"
                           f"Проверьте написание или добавьте новую привычку с помощью /add_habit")

async def reminder():
    while True:

        now_time = datetime.datetime.now()
    
        if now_time.hour == 9 and now_time.minute == 0:
            
            for user_id in ALL_CHATS_ID:
                try:
                    await bot.send_message(chat_id=user_id, text = "привычки - фундамент прогресса, не забывай про них!")
                except:
                    print("Ошибка в напоминалке")

        await asyncio.sleep(30)

    

        


        
            

            
    
async def main():

    asyncio.create_task(reminder())

    await dp.start_polling(bot)


if __name__ == '__main__':
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
        