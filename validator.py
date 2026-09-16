import re
from datetime import datetime, timedelta

from pydantic import BaseModel


class AnalysisResult(BaseModel):
    outcome: str
    next_step: str | None
    next_action_date: str | None
    client_needs: list[str]
    risks: list[str]
    manager_mistakes: list[str]
    manager_attention: list[str]


MONTHS = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}


WEEKDAYS = {
    "понедельник": 0,
    "вторник": 1,
    "среда": 2,
    "четверг": 3,
    "пятница": 4,
    "суббота": 5,
    "воскресенье": 6,
}


def get_transcript_date(transcript: str) -> datetime | None:
    """Извлекает дату разговора из расшифровки."""

    numeric_date = re.search(
        r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b",
        transcript,
    )

    if numeric_date:
        day, month, year = map(int, numeric_date.groups())
        return datetime(year, month, day)

    text_date = re.search(
        r"\b(\d{1,2})\s+"
        r"(января|февраля|марта|апреля|мая|июня|"
        r"июля|августа|сентября|октября|ноября|декабря)"
        r"\s+(\d{4})",
        transcript.lower(),
    )

    if text_date:
        day = int(text_date.group(1))
        month = MONTHS[text_date.group(2)]
        year = int(text_date.group(3))

        return datetime(year, month, day)

    return None


def extract_expected_dates(
    transcript: str,
) -> tuple[list[datetime], list[datetime]]:
    """
    Извлекает даты, которые можно однозначно определить
    из разговора.
    """

    conversation_date = get_transcript_date(transcript)

    if conversation_date is None:
        return [], []

    exact_dates = []
    forbidden_dates = []

    text = transcript.lower()

    if "послезавтра" in text:
        exact_dates.append(
            conversation_date + timedelta(days=2)
        )

    elif "завтра" in text:
        exact_dates.append(
            conversation_date + timedelta(days=1)
        )

    weekday_pattern = (
        r"\bв\s+"
        r"(понедельник|вторник|среду|среда|"
        r"четверг|пятницу|пятница|"
        r"субботу|суббота|воскресенье)"
    )

    for match in re.finditer(weekday_pattern, text):
        weekday_name = match.group(1)

        weekday_name = {
            "среду": "среда",
            "пятницу": "пятница",
            "субботу": "суббота",
        }.get(weekday_name, weekday_name)

        target_weekday = WEEKDAYS[weekday_name]

        days_ahead = (
            target_weekday - conversation_date.weekday()
        ) % 7

        if days_ahead == 0:
            days_ahead = 7

        exact_dates.append(
            conversation_date + timedelta(days=days_ahead)
        )

    date_pattern = (
        r"\b(\d{1,2})\s+"
        r"(января|февраля|марта|апреля|мая|июня|"
        r"июля|августа|сентября|октября|ноября|декабря)\b"
    )

    for match in re.finditer(date_pattern, text):
        day = int(match.group(1))
        month = MONTHS[match.group(2)]

        year = conversation_date.year

        if month < conversation_date.month:
            year += 1

        try:
            found_date = datetime(year, month, day)
        except ValueError:
            continue

        before = text[max(0, match.start() - 20):match.start()]

        if re.search(r"после\s*$", before):
            forbidden_dates.append(found_date)
        else:
            exact_dates.append(found_date)

    return (
        sorted(set(exact_dates)),
        sorted(set(forbidden_dates)),
    )


def validate_result(
    result: dict,
    transcript: str,
) -> list[str]:

    errors = []

    if result is None:
        return ["Модель не вернула результат анализа."]

    try:
        AnalysisResult.model_validate(result)
    except Exception as error:
        errors.append(
            f"Неверная структура JSON: {error}"
        )

    date = result.get("next_action_date")

    if date is None:
        return errors

    try:
        model_date = datetime.strptime(
            date,
            "%Y-%m-%d",
        )
    except ValueError:
        errors.append(
            f"Некорректный формат даты: {date}"
        )
        return errors

    expected_dates, forbidden_dates = extract_expected_dates(
        transcript
    )

    if model_date in forbidden_dates:
        errors.append(
            f"Модель указала {date} как точную дату, "
            f"хотя в разговоре сказано, что действие будет "
            f"после этой даты."
        )

        return errors

    if expected_dates and model_date not in expected_dates:
        expected = ", ".join(
            item.strftime("%Y-%m-%d")
            for item in expected_dates
        )

        errors.append(
            f"Дата {date} не соответствует датам, "
            f"которые можно вывести из разговора. "
            f"Допустимые даты: {expected}"
        )

    return errors