import json
import os

from openpyxl import Workbook


def save_json(result: dict, filename: str) -> None:
    os.makedirs("output/json", exist_ok=True)

    name = os.path.splitext(
        os.path.basename(filename)
    )[0]

    output_path = f"output/json/{name}.json"

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            ensure_ascii=False,
            indent=2,
        )


def save_excel(result: dict, filename: str) -> None:
    os.makedirs("output/excel", exist_ok=True)

    name = os.path.splitext(
        os.path.basename(filename)
    )[0]

    output_path = f"output/excel/{name}.xlsx"

    workbook = Workbook()
    sheet = workbook.active

    sheet.title = "Анализ"

    fields = {
        "Итог": result["outcome"],
        "Следующий шаг": result["next_step"],
        "Дата следующего действия": result["next_action_date"],
        "Потребности клиента": "\n".join(
            result["client_needs"]
        ),
        "Риски": "\n".join(
            result["risks"]
        ),
        "Ошибки менеджера": "\n".join(
            result["manager_mistakes"]
        ),
        "Требует внимания": "\n".join(
            result["manager_attention"]
        ),
    }

    sheet.append(["Поле", "Значение"])

    for field, value in fields.items():
        sheet.append([field, value])

    sheet.column_dimensions["A"].width = 30
    sheet.column_dimensions["B"].width = 80

    for row in sheet.iter_rows():
        for cell in row:
            cell.alignment = cell.alignment.copy(
                wrap_text=True,
                vertical="top",
            )

    workbook.save(output_path)