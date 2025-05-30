import sys
import os

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from docx import Document
from app import create_app, db
from app.models.work_types import WorkType

def import_tariffs(docx_path):
    app = create_app()
    with app.app_context():
        doc = Document(docx_path)
        table = doc.tables[0]  # Предполагается, что таблица с тарифами — первая

        for row in table.rows[1:]:  # Пропускаем заголовок
            cells = row.cells
            try:
                name = cells[1].text.strip()  # Наименование услуги
                unit = cells[2].text.strip()  # Единица измерения
                price = float(cells[3].text.strip().replace(',', '.'))  # Тариф без НДС
                price_with_vat = float(cells[4].text.strip().replace(',', '.'))  # Тариф с НДС

                # Проверяем, существует ли запись
                existing = WorkType.query.filter_by(name=name).first()
                if existing:
                    existing.unit = unit
                    existing.price = price
                    existing.price_with_vat = price_with_vat
                    print(f"Обновлена услуга: {name}")
                else:
                    work_type = WorkType(
                        name=name,
                        unit=unit,
                        price=price,
                        price_with_vat=price_with_vat
                    )
                    db.session.add(work_type)
                    print(f"Добавлена услуга: {name}")
            except ValueError as e:
                print(f"Ошибка в строке '{cells[1].text}': {e}")
                continue
            except IndexError as e:
                print(f"Ошибка в строке: неверная структура таблицы ({e})")
                continue

        db.session.commit()
        print("Импорт тарифов завершен!")

if __name__ == "__main__":
    docx_path = "Тарифы.docx"  # Убедитесь, что файл находится в корне проекта
    import_tariffs(docx_path)