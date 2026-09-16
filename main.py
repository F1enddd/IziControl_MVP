import glob
import os

from analyzer import (
    analyze_transcript,
    retry_analysis,
)
from exporter import (
    save_excel,
    save_json,
)
from validator import validate_result


def process_transcript(filename: str) -> None:
    print(f"Обработка: {filename}")

    with open(
        filename,
        "r",
        encoding="utf-8",
    ) as file:
        transcript = file.read()

    result = analyze_transcript(transcript)

    errors = validate_result(
        result,
        transcript,
    )

    if errors:
        print("  Найдены ошибки валидации. Выполняю retry...")

        result = retry_analysis(
            transcript,
            result,
            errors,
        )

        errors = validate_result(
            result,
            transcript,
        )

        if errors:
            print("  ОШИБКА: retry не прошёл валидацию.")

            for error in errors:
                print(f"    - {error}")

            return

        print("  Retry успешно прошёл валидацию.")

    else:
        print("  Валидация пройдена.")

    save_json(
        result,
        filename,
    )

    save_excel(
        result,
        filename,
    )

    print("  JSON сохранён.")
    print("  Excel сохранён.")


def main() -> None:
    os.makedirs("output", exist_ok=True)

    for filename in glob.glob("transcripts/*.txt"):
        process_transcript(filename)

    print("\nГотово.")


if __name__ == "__main__":
    main()