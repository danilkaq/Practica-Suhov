import pandas as pd


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
