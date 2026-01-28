import asyncio
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

from config import TOKEN
from schedule import report_schedule
from topics import report_topics
from students import report_students
from attendence import report_attendance
from homework import report_homework_checked
from homework_percent import report_homework_submitted

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_state = {}


def menu_text() -> str:
    return (
        "Выберите следующий отчет:\n"
        "/schedule_report — отчет по расписанию\n"
        "/topics_report — отчет по темам занятий\n"
        "/students_report — отчет по студентам\n"
        "/attendance_report — посещаемость\n"
        "/homework_checked — проверка ДЗ\n"
        "/homework_submitted — сдача ДЗ"
    )


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет! 👋\n\n"
        "Я бот для формирования отчетов учебной части.\n\n"
        + menu_text()
    )


#  ЗАДАНИЕ 1
@dp.message(Command("schedule_report"))
async def schedule_cmd(message: types.Message):
    user_state[message.from_user.id] = "schedule"
    await message.answer("📎 Загрузите xls-файл с расписанием группы")


#  ЗАДАНИЕ 2
@dp.message(Command("topics_report"))
async def topics_cmd(message: types.Message):
    user_state[message.from_user.id] = "topics"
    await message.answer("📎 Загрузите xls-файл с темами занятий")


#  ЗАДАНИЕ 3
@dp.message(Command("students_report"))
async def students_cmd(message: types.Message):
    user_state[message.from_user.id] = "students"
    await message.answer("📎 Загрузите xls-файл с отчетом по студентам")


#  ЗАДАНИЕ 4
@dp.message(Command("attendance_report"))
async def attendance_cmd(message: types.Message):
    user_state[message.from_user.id] = "attendance"
    await message.answer("📎 Загрузите xls-файл с посещаемостью преподавателей")


#  ЗАДАНИЕ 5
@dp.message(Command("homework_checked"))
async def homework_checked_cmd(message: types.Message):
    user_state[message.from_user.id] = "homework_checked"
    await message.answer("📎 Загрузите xls-файл с отчетом по проверенным ДЗ")


#  ЗАДАНИЕ 6
@dp.message(Command("homework_submitted"))
async def homework_submitted_cmd(message: types.Message):
    user_state[message.from_user.id] = "homework_submitted"
    await message.answer("📎 Загрузите xls-файл с отчетом по СДАННЫМ ДЗ")


@dp.message(F.document)
async def handle_file(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_state:
        await message.answer("❗ Сначала выберите команду отчета\n\n" + menu_text())
        return

    os.makedirs("files", exist_ok=True)

    file = await bot.get_file(message.document.file_id)
    file_path = f"files/{message.document.file_name}"
    await bot.download_file(file.file_path, file_path)

    task = user_state[user_id]

    try:
        if task == "schedule":
            report = report_schedule(file_path)
            await send_long_message(message, report)

        elif task == "topics":
            report = report_topics(file_path)
            await send_long_message(message, report)

        elif task == "students":
            report = report_students(file_path)
            await send_long_message(message, report)

        elif task == "attendance":
            report = report_attendance(file_path)
            await send_long_message(message, report)

        elif task == "homework_checked":
            report = report_homework_checked(file_path)
            await send_long_message(message, report)

        elif task == "homework_submitted":
            report = report_homework_submitted(file_path)
            await send_long_message(message, report)

        else:
            await message.answer("Задание пока не реализовано")

    except Exception as e:
        await message.answer(f"❌ Ошибка при обработке файла:\n{e}")

    # сброс состояния и показ меню снова
    user_state.pop(user_id, None)
    await message.answer("✅ Готово!\n\n" + menu_text())


async def send_long_message(message: types.Message, text: str):
    MAX_LENGTH = 4000
    for i in range(0, len(text), MAX_LENGTH):
        await message.answer(text[i:i + MAX_LENGTH])


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
