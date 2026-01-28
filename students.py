import pandas as pd


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
