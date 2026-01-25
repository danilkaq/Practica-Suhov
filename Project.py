import asyncio
import os
import pandas as pd

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import re

TOKEN = "8441368486:AAHNEejv0vrWkvpLF_Yk3eJAhhoQkEbeRK4"

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






def report_topics(file_path: str) -> str:
    df = pd.read_excel(file_path, header=None)

    pattern = re.compile(r"^Урок № \d+\. Тема: .+")
    valid_topics = []
    invalid_topics = []

    for row in df.values:
        for cell in row:
            if not isinstance(cell, str):
                continue

            text = cell.strip()


            if "Урок" in text or "Тема" in text:
                if pattern.match(text):
                    valid_topics.append(text)
                else:
                    invalid_topics.append(text)

    if not valid_topics and not invalid_topics:
        return "❌ В файле не найдено тем занятий"

    result = "📘 Отчет по темам занятий\n\n"

    result += "❌ Темы с ОШИБОЧНЫМ форматом:\n"
    if invalid_topics:
        for topic in invalid_topics:
            result += f"• {topic}\n"
    else:
        result += "— отсутствуют\n"

    result += "\n✅ Темы с КОРРЕКТНЫМ форматом:\n"
    if valid_topics:
        for topic in valid_topics:
            result += f"• {topic}\n"
    else:
        result += "— отсутствуют\n"

    return result



def report_students(file_path: str) -> str:
    df = pd.read_excel(file_path)

    required_columns = {"FIO", "Percentage Homework.1", "Classroom"}
    if not required_columns.issubset(df.columns):
        return (
            "❌ В файле должны быть колонки:\n"
            "FIO, Percentage Homework.1, Classroom"
        )

    bad_students = []

    for _, row in df.iterrows():
        try:
            hw_avg = float(row["Percentage Homework.1"])
            classroom = float(row["Classroom"])

            if hw_avg == 1 and classroom <= 3:
                bad_students.append(str(row["FIO"]))
        except:
            continue

    if not bad_students:
        return "✅ Студенты с заданными условиями не найдены"

    result = (
        "📋 Отчет по студентам\n"
        "Средняя оценка за ДЗ = 1\n"
        "Классная работа ≤ 3\n\n"
    )

    for i, student in enumerate(bad_students, 1):
        result += f"{i}. {student}\n"

    return result
def report_attendance(file_path: str) -> str:
    df = pd.read_excel(file_path)

    teacher_col = None
    attendance_col = None

    for col in df.columns:
        name = col.lower()
        if "преподав" in name or "teacher" in name:
            teacher_col = col
        elif "посещ" in name or "attendance" in name or "%" in name:
            attendance_col = col

    if not teacher_col or not attendance_col:
        return "❌ Не удалось определить колонки с преподавателем и посещаемостью"

    bad_teachers = []

    for _, row in df.iterrows():
        try:
            attendance = row[attendance_col]

            if isinstance(attendance, str):
                attendance = attendance.replace("%", "").replace(",", ".")
            attendance = float(attendance)

            # если значение в долях (0.35)
            if attendance <= 1:
                attendance *= 100

            if attendance < 40:
                bad_teachers.append(
                    (str(row[teacher_col]), round(attendance, 1))
                )
        except:
            continue

    if not bad_teachers:
        return "✅ Преподаватели с посещаемостью ниже 40% не найдены"

    result = "📋 Отчет по посещаемости\nПосещаемость ниже 40%\n\n"

    for i, (teacher, percent) in enumerate(bad_teachers, 1):
        result += f"{i}. {teacher} — {percent}%\n"

    return result





def report_homework_checked(file_path: str) -> str:
  
    df = pd.read_excel(file_path, header=[0, 1])

    
    teacher_col = None
    for col in df.columns:
        if str(col[0]).strip().lower() == "фио преподавателя":
            teacher_col = col
            break
    if teacher_col is None:
        return "❌ Не нашёл колонку «ФИО преподавателя»"

    def get_col(section: str, name: str):
        
        for col in df.columns:
            if str(col[0]).strip().lower() == section.lower() and str(col[1]).strip().lower() == name.lower():
                return col
        return None

    month_received_col = get_col("Месяц", "Получено")
    month_checked_col  = get_col("Месяц", "Проверено")
    week_received_col  = get_col("Неделя", "Получено")
    week_checked_col   = get_col("Неделя", "Проверено")

    if not all([month_received_col, month_checked_col, week_received_col, week_checked_col]):
        return (
            "❌ Не нашёл нужные колонки в блоках «Месяц» и «Неделя».\n"
            "Нужно: Получено и Проверено в обоих блоках."
        )

    def build_bad_list(received_col, checked_col):
        bad = []
        for _, row in df.iterrows():
            teacher = row.get(teacher_col, None)
            if pd.isna(teacher):
                continue

            received = row.get(received_col, None)
            checked = row.get(checked_col, None)

            received = pd.to_numeric(received, errors="coerce")
            checked = pd.to_numeric(checked, errors="coerce")

            if pd.isna(received) or pd.isna(checked) or received <= 0:
                continue

            pct = (checked / received) * 100
            if pct < 70:
                bad.append((str(teacher).strip(), int(received), int(checked), round(pct, 1)))

        # отсортируем по возрастанию процента (самые проблемные сверху)
        bad.sort(key=lambda x: x[3])
        return bad

    bad_month = build_bad_list(month_received_col, month_checked_col)
    bad_week = build_bad_list(week_received_col, week_checked_col)

    if not bad_month and not bad_week:
        return "✅ Нет преподавателей с проверкой ДЗ ниже 70% (и за месяц, и за неделю)."

    result = "📋 Отчет по проверенным домашним заданиям (порог < 70%)\n\n"

    result += "🗓️ Месяц:\n"
    if bad_month:
        for i, (t, rec, chk, pct) in enumerate(bad_month, 1):
            result += f"{i}. {t} — {pct}% (Проверено {chk} из {rec})\n"
    else:
        result += "— нет нарушений\n"

    result += "\n📆 Неделя:\n"
    if bad_week:
        for i, (t, rec, chk, pct) in enumerate(bad_week, 1):
            result += f"{i}. {t} — {pct}% (Проверено {chk} из {rec})\n"
    else:
        result += "— нет нарушений\n"

    return result







async def send_long_message(message: types.Message, text: str):
    MAX_LENGTH = 4000

    for i in range(0, len(text), MAX_LENGTH):
        await message.answer(text[i:i + MAX_LENGTH])


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
