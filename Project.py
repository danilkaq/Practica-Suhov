import asyncio
import os
import pandas as pd

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

TOKEN = "8441368486:AAEzszhElzO5vmXrYferEwcQ0n5BiwXdHZw"

bot = Bot(token=TOKEN)
dp = Dispatcher()


user_state = {}


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет! 👋\n\n"
        "Я бот для формирования отчетов учебной части.\n\n"
        "Команды:\n"
        "/schedule_report — отчет по расписанию\n"
        "/topics_report — отчет по темам занятий\n"
        "/students_report — отчет по студентам\n"
        "/attendance_report — посещаемость\n"
        "/homework_checked — проверка ДЗ\n"
        "/homework_submitted — сдача ДЗ"
    )


#  ЗАДАНИЕ 1
@dp.message(Command("schedule_report"))
async def schedule_cmd(message: types.Message):
    user_state[message.from_user.id] = "schedule"
    await message.answer("📎 Загрузите xls-файл с расписанием группы")



@dp.message(F.document)
async def handle_file(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_state:
        await message.answer("❗ Сначала выберите команду отчета")
        return

    os.makedirs("files", exist_ok=True)

    file = await bot.get_file(message.document.file_id)
    file_path = f"files/{message.document.file_name}"
    await bot.download_file(file.file_path, file_path)

    task = user_state[user_id]

    try:
        if task == "schedule":
            report = report_schedule(file_path)
            await message.answer(report)
        else:
            await message.answer("Задание пока не реализовано")

    except Exception as e:
        await message.answer(f"❌ Ошибка при обработке файла:\n{e}")

    user_state.pop(user_id)



def report_schedule(file_path: str) -> str:
    df = pd.read_excel(file_path, header=None)

    subjects = []

    for row in df.values:
        for cell in row:
            if isinstance(cell, str) and "Предмет:" in cell:
                subject = cell.split("Предмет:")[1].strip()
                if subject:
                    subjects.append(subject)

    if not subjects:
        return "❌ Не удалось найти предметы в файле"

    counts = {}
    for s in subjects:
        counts[s] = counts.get(s, 0) + 1

    text = "📘 Отчет по расписанию группы:\n\n"
    for subject, count in counts.items():
        text += f"{subject} — {count} пар\n"

    return text



async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
