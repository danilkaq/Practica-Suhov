import pandas as pd


def report_homework_submitted(file_path: str) -> str:
    df = pd.read_excel(file_path)

    required_columns = {"FIO", "Percentage Homework"}
    if not required_columns.issubset(df.columns):
        return (
            "❌ В файле должны быть колонки:\n"
            "FIO, Percentage Homework"
        )

    bad_students = []

    for _, row in df.iterrows():
        fio = row.get("FIO")
        val = row.get("Percentage Homework")

        if pd.isna(fio) or pd.isna(val):
            continue

        try:
            # поддержка "65%", "65,5", 0.65, 65
            if isinstance(val, str):
                val = val.replace("%", "").replace(",", ".").strip()

            percent = float(val)


            if percent <= 1:
                percent *= 100

            if percent < 70:
                bad_students.append((str(fio).strip(), round(percent, 1)))
        except:
            continue

    if not bad_students:
        return "✅ Нет студентов с % выполненных ДЗ ниже 70%"

    bad_students.sort(key=lambda x: x[1])

    result = "📋 Отчет по сданным домашним заданиям\n% выполненных ДЗ ниже 70%\n\n"
    for i, (fio, pct) in enumerate(bad_students, 1):
        result += f"{i}. {fio} — {pct}%\n"

    return result
