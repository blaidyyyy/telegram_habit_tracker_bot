import aiogram
import asyncio
import json
import datetime
from datetime import date
import random
import os


from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message

from config import TOKEN

bot = Bot(token = TOKEN)
dp = Dispatcher()

DB_HABITS = "habits.json"

async def load_file():

    if (os.path.exists(DB_HABITS)):
        try:
            with open(DB_HABITS, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data
        except Exception as e:
            print(f"ошибка {e} в load_file")
            return {"users" : {}}
    else:
         return {"users" : {}}   
    
async def save_file(data):
    try:
        with open(DB_HABITS, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    except Exception as e:
            print(f"ошибка {e} в save_file")
            
                
        
            
    


@dp.message(CommandStart())
async def cmd_start(message : Message):

    await message.answer("Привет! Я твой трекер привычек.\n\n"
        "Доступные команды:\n"
        "/add_habit + название привычки - добавить привычку\n"
        "/list_habits - список привычек\n"
        "/complete + название привычки - отметить выполнение\n" \
        "/delete + название привычки - удалить привычку"
  
    )



@dp.message(Command("list_habits"))
async def list_of_habits(message : Message):
    user_id = str(message.from_user.id)
    data = await load_file()

    if user_id not in data.get("users", {}) or not data["users"][user_id]["habits"]:
        await message.answer("У вас пока нет привычек! Добавьте первую с помощью /add_habit")
        return

    user_habits = data["users"][user_id]["habits"]
    
    habits_list = "📋 Ваши привычки:\n\n"
    
    for i, habit in enumerate(user_habits, 1):
        name = habit['name']
        streak = habit['streak']
        lives = "".join(habit.get('system_of_lives', []))
        lives_display = lives if lives else "💀 (жизней нет)"
        
        
        habits_list += f"{i}. {name} - Стрик: {streak} \nЖизни: {lives_display}\n\n"

    await message.answer(habits_list)


def get_lives_str(lives_list):
    return "".join(lives_list)

@dp.message(Command("add_habit"))
async def add_habit_command(message : Message, command : CommandObject ):
    habit_name = command.args
    user_id = str(message.from_user.id)

    if not habit_name:
        await message.answer(" Укажите название привычки!\n")
        return
    
    data = await load_file()
    
    if user_id not in data["users"]:
        data["users"][user_id] = {"habits": []}
    
    
    for habit in data["users"][user_id]["habits"]:
        if habit["name"].lower() == habit_name.lower():
            await message.answer(f"Привычка '{habit_name}' уже существует!")
            return
    
    
    new_habit = {"name": habit_name, "streak": 0, "last_completed": None, "system_of_lives":["❤️","❤️","❤️"] }
    data["users"][user_id]["habits"].append(new_habit)
    
    
    

    await save_file(data)
    
    await message.answer(f"Привычка '{habit_name}' добавлена! ✅\nВаши жизни:❤️❤️❤️")


@dp.message(Command("complete"))
async def complete_habit(message : Message, command : CommandObject ):
    user_id = str(message.from_user.id)
    habit_name = command.args

    if not habit_name:
        await message.answer("Укажите название привычки!")
        return
    
    data = await load_file()

    if user_id not in data.get("users", {}):

        await message.answer("Сначала нужно добавить привычки! Используйте функцию /add_habit")
        return
    

    habit_found = False
    today = datetime.datetime.now().date().isoformat()      
    for habit in data["users"][user_id]["habits"]:

        if habit["name"].lower() == habit_name.lower():
            habit_found = True

            if habit.get("last_completed") == today:
                await message.answer(f" Вы уже отмечали привычку '{habit_name}' сегодня!")
                return
            habit["streak"] += 1
            habit["last_completed"] = today

            await save_file(data)
            
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


            if now.hour == 0 and now.minute > 1:

                data = await load_file()
                today = date.today()
                
                for user_id, user_data in data.get("users", {}).items():
                     for habit in user_data.get("habits", []):
                        last_completed = habit.get("last_completed")
                        if last_completed:
                            try:
                                last_date = date.fromisoformat(last_completed)
                                days_missed = (today - last_date).days

                                if days_missed >= 1:
                                    
                                    if len(habit.get("system_of_lives", [])) > 0:
                                        habit["system_of_lives"].pop()
                                        changes_made = True
                                    
                                        
                                        await bot.send_message(
                                        chat_id=int(user_id),
                                        text=f"⚠️ Пропуск! Привычка: {habit['name']}\nЖизни: {''.join(habit['system_of_lives'])}"
                                        )
                            

                               
                                    if len(habit["system_of_lives"]) == 0:
                                        habit["streak"] = 0
                                        habit["system_of_lives"] = ["❤️", "❤️", "❤️"]
                                        changes_made = True
                                        await bot.send_message(chat_id=int(user_id), text=f"Вы не отмечали привычку <{habit['name']}> три дня. Стрик обнулен!💀")

                            except Exception:
                                    print("ошибка в m_d_ch")

                                         
                                
            if changes_made and data is not None:
                   
                await save_file(data)

            

        except Exception as e:
            print(f"ищи ошибку в missed_days_check: {e}")


            
@dp.message(Command("delete"))
async def delete_habit(message : Message,command : CommandObject ):
    user_id = str(message.from_user.id)
    habit_name = command.args

    if not habit_name:
                await message.answer(" Укажите название привычки!\n")
                return

    data = await load_file()

    if user_id not in data.get("users", {}):
        await message.answer(" У вас ещё нет привычек! Используйте функцию /add_habit, чтобы создать их.")
        return

        

    habit_found = False
    for i, habit in enumerate(data["users"][user_id]["habits"]):
        if habit["name"].lower() == habit_name.lower():
            
            habit_found = True

            del data["users"][user_id]["habits"][i]

            await save_file(data)
            await message.answer(f"Привычка '{habit_name}' удалена! ✅")
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
                "Привычки - фундамент прогресса, не забывай про них!",
                "Шаги превращают мечты в цели!",
                "Сегодняшние усилия - завтрашние победы!",
                "Каждая отмеченная привычка - шаг к лучшей версии себя.",
                "Даже один день имеет значение!",
                "Привычки формируют характер, характер - судьбу. ⭐"
            ]
        

async def reminder():
    while True:

        await asyncio.sleep(60)

        now_time = datetime.datetime.now()
    
        if now_time.hour == 9 and now_time.minute == 00:
            try:

                data = await load_file()

                users = data.get("users", {})

                for user_id in users:
                    user_id_int = int(user_id)
                    random_quote = random.choice(motivational_quotes)
                    await bot.send_message(chat_id=user_id_int, text = f" Доброе утро!\n\n{random_quote}\n")

  
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

        