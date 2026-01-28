import pandas as pd


def report_attendance(file_path: str) -> str:
    df = pd.read_excel(file_path)

    teacher_col = None
    attendance_col = None

    for col in df.columns:
        name = str(col).lower()
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
                bad_teachers.append((str(row[teacher_col]), round(attendance, 1)))
        except:
            continue

    if not bad_teachers:
        return "✅ Преподаватели с посещаемостью ниже 40% не найдены"

    result = "📋 Отчет по посещаемости\nПосещаемость ниже 40%\n\n"

    for i, (teacher, percent) in enumerate(bad_teachers, 1):
        result += f"{i}. {teacher} — {percent}%\n"

    return result
