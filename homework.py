import pandas as pd


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
            if (
                str(col[0]).strip().lower() == section.lower()
                and str(col[1]).strip().lower() == name.lower()
            ):
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
