import aiogram
import asyncio
import json
import datetime
import random


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
        "/complete + название привычки - отметить выполнение\n" \
        "/delete + назывние привычки - удалить привычку"

        
        
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

    if not habit_name:
        await message.answer("❌ Укажите название привычки!\n")
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
    
    
    new_habit = {"name": habit_name, "streak": 0, "last_completed": None}
    data["users"][user_id]["habits"].append(new_habit)
    
    

    with open('habits.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    
    await message.answer(f"Привычка '{habit_name}' добавлена! ✅")


@dp.message(Command("complete"))
async def complete_habit(message : Message):
    user_id = str(message.from_user.id)
    habit_name = message.text.replace('/complete', '').strip()

    if not habit_name:
        await message.answer("Укажите название привычки!")
        return
    
    with open('habits.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

    if user_id not in data.get("users", {}):

        await message.answer("Сначала нужно добавить привычки! Используйте функцию /add_habit")
        return
    

    habit_found = False
    today = datetime.datetime.now().date().isoformat()      
    for habit in data["users"][user_id]["habits"]:

        if habit["name"].lower() == habit_name.lower():
            habit_found = True

            if habit.get("last_completed") == today:
                await message.answer(f"✅ Вы уже отмечали привычку '{habit_name}' сегодня!")
                return
            habit["streak"] += 1
            habit["last_completed"] = today

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
        
async def missed_days_check():
    while True:
        try:
            await asyncio.sleep(60)
            now = datetime.datetime.now()

            changes_made = False
            data = None

            if now.hour == 0 and now.minute < 1:

                with open('habits.json','r', encoding='utf-8') as file:
                    data = json.load(file)
                today = datetime.datetime.now().date()
                
                for user_id, user_data in data.get("users", {}).items():
                     for habit in user_data.get("habits", []):
                        last_completed = habit.get("last_completed")
                        if last_completed:
                            try:
                                last_date = datetime.datetime.fromisoformat(last_completed).date()
                                days_missed = (today - last_date).days

                                if days_missed >= 2:
                                    
                                    if habit.get("streak", 0) > 0:
                                        habit["streak"] = 0
                                        changes_made = True

                                        await bot.send_message(
                                            chat_id=int(user_id),
                                            text=f"⚠️ Привычка '{habit['name']}' сброшена!\n"
                                                 f"Количество пропущенных дней {days_missed}.\n"
                                        )
                            except:
                                pass
            if changes_made and data is not None:
                   
                with open('habits.json', 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=2)

            

        except Exception as e:
            print(f"ищи ошибку в missed_days_check: {e}")


            
@dp.message(Command("delete"))
async def delete_habit(message : Message):
    user_id = str(message.from_user.id)
    habit_name = message.text.replace('/delete', '').strip()

    if not habit_name:
                await message.answer("❌ Укажите название привычки!\n")
                return

    with open('habits.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    if user_id not in data.get("users", {}):
        await message.answer("❌ У вас ещё нет привычек!")
        return

        

    habit_found = False
    for i, habit in enumerate(data["users"][user_id]["habits"]):
        if habit["name"].lower() == habit_name.lower():
            
            habit_found = True

            del data["users"][user_id]["habits"][i]

            with open('habits.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
                await message.answer(f"✅ Привычка '{habit_name}' удалена!")
                break
    if not habit_found:
        
        if data["users"][user_id]["habits"]:
            habits_list = "\n".join([f" {h['name']}" for h in data["users"][user_id]["habits"]])
            await message.answer(
            f"❌ Привычка '{habit_name}' не найдена!\n\n"
            f"📋 Ваши привычки:\n{habits_list}"
            )
        else:
            await message.answer(
                f"❌ Привычка '{habit_name}' не найдена!\n"
                f"У вас нет привычек."
            )


motivational_quotes = [
                "Привычки - фундамент прогресса, не забывай про них! 💪",
                "Маленькие шаги каждый день приводят к большим результатам! 🚀",
                "Сегодняшние усилия - завтрашние победы! ✨",
                "Не пропускай ни дня, именно так формируются сильные привычки! 🔥",
                "Каждая отмеченная привычка - шаг к лучшей версии себя! 🌟",
                "Последовательность - ключ к успеху в формировании привычек! 🗝️",
                "Даже один день имеет значение! Открой приложение и отметь свои привычки! 📱",
                "Сила воли как мышца - тренируй ее каждый день! 💫",
                "Твой будущий я благодарит тебя за сегодняшние усилия! 🙏",
                "Привычки формируют характер, характер определяет судьбу! ⭐"
            ]
        

async def reminder():
    while True:

        await asyncio.sleep(30)

        now_time = datetime.datetime.now()
    
        if now_time.hour == 9 and now_time.minute == 00:
            try:
                with open('habits.json', 'r', encoding='utf-8') as file:

                    data = json.load(file)

                    users = data.get("users", {})

                    for user_id in users:
                        user_id_int = int(user_id)
                        random_quote = random.choice(motivational_quotes)
                        await bot.send_message(chat_id=user_id_int, text = f"🌅 Доброе утро! 🌅\n\n{random_quote}\n")

                
                   
                

            except Exception as e:
                print(f"ищи ошибку в reminder'е: {e}")
        
            
  
async def main():
    await asyncio.gather(
        dp.start_polling(bot),
        reminder(),
        missed_days_check()
    )



if __name__ == '__main__':
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")

        