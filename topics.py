import pandas as pd
import re


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
