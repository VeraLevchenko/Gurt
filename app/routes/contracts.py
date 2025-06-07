from flask import Blueprint, render_template, request, redirect, url_for, send_file
from .. import db
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError
import re
import io
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import os
from werkzeug.utils import secure_filename
from ..models.contracts import Contract, contract_documents, contract_additional_files
from ..models.work_types import WorkType
from ..models.physical_person import PhysicalPerson
from ..models.legal_entity import LegalEntity
from uuid import uuid4
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

bp = Blueprint('contracts', __name__, url_prefix='/contracts')

# Разрешенные типы файлов
ALLOWED_EXTENSIONS = {'.pdf', '.docx'}

def allowed_file(filename):
    """Проверяет, имеет ли файл разрешенное расширение."""
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

def validate_contract_number(number):
    """Проверяет, соответствует ли номер договора формату 08-0/XXXXX."""
    return bool(re.match(r'^08-0/\d+$', number))

def generate_unique_filename(filename):
    """Генерирует уникальное имя файла с префиксом UUID."""
    ext = os.path.splitext(filename)[1].lower()
    unique_name = f"{uuid4()}{ext}"
    unique_name = secure_filename(unique_name)
    if len(unique_name) > 255:
        raise ValueError(f"Сгенерированное имя файла слишком длинное: {unique_name}")
    return unique_name

@bp.route('/')
def list_contracts():
    contracts = Contract.query.all()
    return render_template('contracts/list.html', contracts=contracts)

@bp.route('/download_excel')
def download_excel():
    contracts = Contract.query.all()
    wb = Workbook()
    ws = wb.active
    ws.title = "Договоры"
    headers = ['Номер', 'Дата', 'Субъект', 'Цена', 'Адрес', 'Объект', 'Наименование работ']
    for col_num, header in enumerate(headers, 1):
        ws[f'{get_column_letter(col_num)}1'] = header
    for row_num, contract in enumerate(contracts, 2):
        ws[f'A{row_num}'] = contract.number
        ws[f'B{row_num}'] = contract.contract_date.strftime('%Y-%m-%d')
        ws[f'C{row_num}'] = contract.get_subject()
        ws[f'D{row_num}'] = contract.price
        ws[f'E{row_num}'] = contract.address
        ws[f'F{row_num}'] = contract.object_name
        ws[f'G{row_num}'] = '; '.join([f"{wt.name} ({wt.price} руб.)" for wt in contract.work_types])
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='contracts.xlsx'
    )

@bp.route('/<int:id>')
def contract_detail(id):
    contract = Contract.query.get_or_404(id)
    return render_template('contracts/detail.html', contract=contract, edit_mode=False)

@bp.route('/download_file/<path:filename>')
def download_file(filename):
    try:
        return send_file(os.path.join('uploads', filename), as_attachment=True)
    except FileNotFoundError:
        return "Файл не найден", 404

@bp.route('/create', methods=['GET', 'POST'])
def create_contract():
    if request.method == "POST":
        try:
            number = request.form['number'].strip()
            logging.debug(f"Попытка создать договор с параметрами: number={number}, form_data={request.form.to_dict()}")
            if not validate_contract_number(number):
                raise ValueError("Номер договора должен быть в формате 08-0/XXXXX, где XXXXX - число")
            
            db.session.flush()
            db.session.expire_all()
            existing_contract = Contract.query.filter_by(number=number).first()
            if existing_contract:
                raise ValueError(f"Номер договора '{number}' уже существует (ID: {existing_contract.id})")

            object_name = request.form['object_name'].strip()
            if not object_name:
                raise ValueError("Поле 'Объект' не может быть пустым")
            
            selected_work_type_ids = request.form.getlist('work_description')
            logging.debug(f"Выбранные ID типов работ: {selected_work_type_ids}")
            if not selected_work_type_ids:
                raise ValueError("Не выбрано ни одного типа работ")
            work_types = WorkType.query.filter(WorkType.id.in_(selected_work_type_ids)).all()
            if not work_types:
                raise ValueError("Выбранные типы работ не найдены в базе данных")
            logging.debug(f"Найденные типы работ: {[wt.name for wt in work_types]}")
            
            total_price = sum(work_type.price for work_type in work_types)
            
            subject_type = request.form.get('subject_type')
            subject_id = request.form.get('subject_id')
            if not subject_type or not subject_id:
                raise ValueError("Не выбран субъект договора")
            
            if subject_type == 'physical':
                subject = PhysicalPerson.query.get(subject_id)
                if not subject:
                    raise ValueError(f"Физическое лицо с ID {subject_id} не найдено")
            elif subject_type == 'legal':
                subject = LegalEntity.query.get(subject_id)
                if not subject:
                    raise ValueError(f"Юридическое лицо с ID {subject_id} не найдено")
            else:
                raise ValueError("Неверный тип субъекта")

            # Обработка вложений документов
            documents = request.files.getlist('documents')
            if len(documents) > 4:
                raise ValueError("Максимум 4 файла для документов")
            document_paths = []
            for file in documents:
                if file and file.filename:
                    if not allowed_file(file.filename):
                        raise ValueError("Разрешены только файлы PDF и DOCX")
                    unique_name = generate_unique_filename(file.filename)
                    file_path = os.path.join('uploads', unique_name)
                    file.save(file_path)
                    document_paths.append(unique_name)
                    logging.debug(f"Сохранен файл документа: {file_path}")

            # Обработка дополнительных вложений
            additional_files = request.files.getlist('additional_files')
            if len(additional_files) > 10:
                raise ValueError("Максимум 10 дополнительных файлов")
            additional_file_paths = []
            for file in additional_files:
                if file and file.filename:
                    if not allowed_file(file.filename):
                        raise ValueError("Разрешены только файлы PDF и DOCX")
                    unique_name = generate_unique_filename(file.filename)
                    file_path = os.path.join('uploads', unique_name)
                    file.save(file_path)
                    additional_file_paths.append(unique_name)
                    logging.debug(f"Сохранен дополнительный файл: {file_path}")

            # Создание договора
            contract = Contract(
                number=number,
                contract_date=datetime.strptime(request.form['contract_date'], '%Y-%m-%d').date(),
                price=total_price,
                address=request.form['address'].strip(),
                object_name=object_name
            )
            if subject_type == 'physical':
                contract.physical_person_id = subject_id
            elif subject_type == 'legal':
                contract.legal_entity_id = subject_id
            contract.work_types = work_types  # Добавляем виды работ
            db.session.add(contract)
            db.session.flush()
            logging.debug(f"Создан контракт с ID: {contract.id}, work_types={[wt.name for wt in contract.work_types]}")

            # Сохранение путей к документам
            for path in document_paths:
                logging.debug(f"Вставка документа: contract_id={contract.id}, file_path={path}")
                db.session.execute(
                    contract_documents.insert().values(contract_id=contract.id, file_path=path)
                )

            # Сохранение путей к дополнительным файлам
            for path in additional_file_paths:
                logging.debug(f"Вставка дополнительного файла: contract_id={contract.id}, file_path={path}")
                db.session.execute(
                    contract_additional_files.insert().values(contract_id=contract.id, file_path=path)
                )

            db.session.commit()
            logging.debug(f"Создан договор {number} с файлами: documents={document_paths}, additional={additional_file_paths}, work_types={[wt.name for wt in work_types]}")
            return redirect(url_for('contracts.list_contracts'))

        except ValueError as e:
            db.session.rollback()
            logging.error(f"ValueError in create_contract: {str(e)}")
            work_types = WorkType.query.all()
            form_data = {
                'number': request.form.get('number', ''),
                'contract_date': request.form.get('contract_date', date.today().strftime('%Y-%m-%d')),
                'address': request.form.get('address', ''),
                'object_name': request.form.get('object_name', ''),
                'selected_work_types': selected_work_type_ids,
                'subject_type': request.form.get('subject_type', ''),
                'subject_id': request.form.get('subject_id', ''),
                'subject_name': request.form.get('subject_name', ''),
                'document_names': [f.filename for f in request.files.getlist('documents') if f.filename],
                'additional_file_names': [f.filename for f in request.files.getlist('additional_files') if f.filename]
            }
            return render_template('contracts/create.html', error=str(e), work_types=work_types, form_data=form_data)
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"IntegrityError in create_contract: {str(e)}")
            work_types = WorkType.query.all()
            form_data = {
                'number': request.form.get('number', ''),
                'contract_date': request.form.get('contract_date', date.today().strftime('%Y-%m-%d')),
                'address': request.form.get('address', ''),
                'object_name': request.form.get('object_name', ''),
                'selected_work_types': selected_work_type_ids,
                'subject_type': request.form.get('subject_type', ''),
                'subject_id': request.form.get('subject_id', ''),
                'subject_name': request.form.get('subject_name', ''),
                'document_names': [f.filename for f in request.files.getlist('documents') if f.filename],
                'additional_file_names': [f.filename for f in request.files.getlist('additional_files') if f.filename]
            }
            error_message = "Ошибка при сохранении вложений"
            if "unique constraint" in str(e).lower() and "number" in str(e).lower():
                error_message = f"Номер договора '{number}' уже существует"
            elif "foreign key" in str(e).lower():
                error_message = f"Ошибка: субъект договора с ID {subject_id} не найден"
            elif "contract_documents" in str(e).lower():
                error_message = f"Ошибка: документ с именем {path} уже существует для договора"
            elif "contract_additional_files" in str(e).lower():
                error_message = f"Ошибка: дополнительный файл с именем {path} уже существует для договора"
            return render_template('contracts/create.html', error=error_message, work_types=work_types, form_data=form_data)
        except Exception as e:
            db.session.rollback()
            logging.error(f"Unexpected error in create_contract: {str(e)}")
            work_types = WorkType.query.all()
            form_data = {
                'number': request.form.get('number', ''),
                'contract_date': request.form.get('contract_date', date.today().strftime('%Y-%m-%d')),
                'address': request.form.get('address', ''),
                'object_name': request.form.get('object_name', ''),
                'selected_work_types': selected_work_type_ids,
                'subject_type': request.form.get('subject_type', ''),
                'subject_id': request.form.get('subject_id', ''),
                'subject_name': request.form.get('subject_name', ''),
                'document_names': [f.filename for f in request.files.getlist('documents') if f.filename],
                'additional_file_names': [f.filename for f in request.files.getlist('additional_files') if f.filename]
            }
            return render_template('contracts/create.html', error=f"Неизвестная ошибка: {str(e)}", work_types=work_types, form_data=form_data)

    work_types = WorkType.query.all()
    contracts = Contract.query.all()
    default_number = '08-0/30000'
    max_suffix = 0
    for contract in contracts:
        if contract.number.startswith('08-0/'):
            try:
                suffix = int(contract.number.split('/')[-1])
                max_suffix = max(max_suffix, suffix)
            except ValueError:
                continue
    if max_suffix >= 30000:
        default_number = f'08-0/{max_suffix + 1}'
    form_data = {
        'number': default_number,
        'contract_date': date.today().strftime('%Y-%m-%d'),
        'address': '',
        'object_name': '',
        'selected_work_types': [],
        'subject_type': '',
        'subject_id': '',
        'subject_name': '',
        'document_names': [],
        'additional_file_names': []
    }
    return render_template('contracts/create.html', work_types=work_types, form_data=form_data)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_contract(id):
    contract = Contract.query.get_or_404(id)
    if request.method == 'POST':
        try:
            number = request.form['number']
            if not validate_contract_number(number):
                raise ValueError("Номер договора должен быть в формате 08-0/XXXXX, где XXXXX - число")
            object_name = request.form['object_name']
            if not object_name:
                raise ValueError("Поле 'Объект' не может быть пустым")
            selected_work_type_ids = request.form.getlist('work_description')
            if not selected_work_type_ids:
                raise ValueError("Не выбрано ни одного типа работ")
            work_types = WorkType.query.filter(WorkType.id.in_(selected_work_type_ids)).all()
            if not work_types:
                raise ValueError("Выбранные типы работ не найдены в базе данных")
            subject_type = request.form.get('subject_type')
            subject_id = request.form.get('subject_id')
            if not subject_type or not subject_id:
                raise ValueError("Не выбран субъект договора")

            contract.contract_date = datetime.strptime(request.form['contract_date'], '%Y-%m-%d').date()
            contract.price = sum(work_type.price for work_type in work_types)
            contract.address = request.form['address']
            contract.object_name = object_name
            contract.physical_person_id = None
            contract.legal_entity_id = None
            if subject_type == 'physical':
                contract.physical_person_id = subject_id
            elif subject_type == 'legal':
                contract.legal_entity_id = subject_id
            else:
                raise ValueError("Неверный тип субъекта")
            contract.work_types = work_types

            if contract.number != number:
                existing_contract = Contract.query.filter_by(number=number).first()
                if existing_contract and existing_contract.id != contract.id:
                    raise ValueError("Номер договора уже существует")
                contract.number = number

            db.session.commit()

            old_document_paths = contract.document_paths.copy()
            documents = request.files.getlist('documents')
            document_paths = old_document_paths.copy()
            if len(documents) + len(document_paths) > 4:
                raise ValueError("Общее количество файлов документов не должно превышать 4")
            new_document_paths = []
            for file in documents:
                if file and file.filename:
                    if not allowed_file(file.filename):
                        raise ValueError("Разрешены только PDF и DOCX")
                    unique_name = generate_unique_filename(file.filename)
                    file_path = os.path.join('uploads', unique_name)
                    file.save(file_path)
                    new_document_paths.append(unique_name)
            document_paths.extend(new_document_paths)

            old_additional_file_paths = contract.additional_file_paths.copy()
            additional_files = request.files.getlist('additional_files')
            additional_file_paths = old_additional_file_paths.copy()
            if len(additional_files) + len(additional_file_paths) > 10:
                raise ValueError("Общее количество дополнительных файлов не должно превышать 10")
            new_additional_file_paths = []
            for file in additional_files:
                if file and file.filename:
                    if not allowed_file(file.filename):
                        raise ValueError("Разрешены только PDF и DOCX")
                    unique_name = generate_unique_filename(file.filename)
                    file_path = os.path.join('uploads', unique_name)
                    file.save(file_path)
                    new_additional_file_paths.append(unique_name)
            additional_file_paths.extend(new_additional_file_paths)

            db.session.execute(
                contract_documents.delete().where(contract_documents.c.contract_id == contract.id)
            )
            db.session.execute(
                contract_additional_files.delete().where(contract_additional_files.c.contract_id == contract.id)
            )

            for path in document_paths:
                db.session.execute(
                    contract_documents.insert().values(contract_id=contract.id, file_path=path)
                )

            for path in additional_file_paths:
                db.session.execute(
                    contract_additional_files.insert().values(contract_id=contract.id, file_path=path)
                )

            for old_path in old_document_paths:
                if old_path not in document_paths:
                    try:
                        os.remove(os.path.join('uploads', old_path))
                        logging.debug(f"Удален файл: {old_path}")
                    except FileNotFoundError:
                        logging.warning(f"Файл не найден для удаления: {old_path}")
            for old_path in old_additional_file_paths:
                if old_path not in additional_file_paths:
                    try:
                        os.remove(os.path.join('uploads', old_path))
                        logging.debug(f"Удален файл: {old_path}")
                    except FileNotFoundError:
                        logging.warning(f"Файл не найден для удаления: {old_path}")

            db.session.commit()
            logging.debug(f"Договор {contract.number} успешно обновлен с файлами: {document_paths}, {additional_file_paths}")

            return redirect(url_for('contracts.contract_detail', id=contract.id))

        except ValueError as e:
            db.session.rollback()
            logging.error(f"ValueError in edit_contract: {str(e)}")
            work_types = WorkType.query.all()
            form_data = {
                'number': request.form.get('number', contract.number),
                'contract_date': request.form.get('contract_date', contract.contract_date.strftime('%Y-%m-%d')),
                'address': request.form.get('address', contract.address),
                'object_name': request.form.get('object_name', contract.object_name),
                'selected_work_types': selected_work_type_ids,
                'subject_type': request.form.get('subject_type', ''),
                'subject_id': request.form.get('subject_id', ''),
                'subject_name': request.form.get('subject_name', '')
            }
            return render_template('contracts/detail.html', contract=contract, edit_mode=True,
                                   error=str(e), work_types=work_types, form_data=form_data)
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"IntegrityError in edit_contract: {str(e)}")
            work_types = WorkType.query.all()
            form_data = {
                'number': request.form.get('number', contract.number),
                'contract_date': request.form.get('contract_date', contract.contract_date.strftime('%Y-%m-%d')),
                'address': request.form.get('address', contract.address),
                'object_name': request.form.get('object_name', contract.object_name),
                'selected_work_types': selected_work_type_ids,
                'subject_type': request.form.get('subject_type', ''),
                'subject_id': request.form.get('subject_id', ''),
                'subject_name': request.form.get('subject_name', '')
            }
            error_message = "Ошибка сохранения: проверьте уникальность данных"
            if "unique constraint" in str(e).lower() and "number" in str(e).lower():
                error_message = "Номер договора уже существует"
            return render_template('contracts/detail.html', contract=contract, edit_mode=True,
                                   error=error_message, work_types=work_types, form_data=form_data)
        except Exception as e:
            db.session.rollback()
            logging.error(f"Unexpected error in edit_contract: {str(e)}")
            work_types = WorkType.query.all()
            form_data = {
                'number': request.form.get('number', contract.number),
                'contract_date': request.form.get('contract_date', contract.contract_date.strftime('%Y-%m-%d')),
                'address': request.form.get('address', contract.address),
                'object_name': request.form.get('object_name', contract.object_name),
                'selected_work_types': selected_work_type_ids,
                'subject_type': request.form.get('subject_type', ''),
                'subject_id': request.form.get('subject_id', ''),
                'subject_name': request.form.get('subject_name', '')
            }
            return render_template('contracts/detail.html', contract=contract, edit_mode=True,
                                   error=f"Неизвестная ошибка: {str(e)}", work_types=work_types, form_data=form_data)

    work_types = WorkType.query.all()
    form_data = {
        'number': contract.number,
        'contract_date': contract.contract_date.strftime('%Y-%m-%d'),
        'address': contract.address,
        'object_name': contract.object_name,
        'selected_work_types': [str(work_type.id) for work_type in contract.work_types],
        'subject_type': 'physical' if contract.physical_person_id else 'legal' if contract.legal_entity_id else '',
        'subject_id': contract.physical_person_id or contract.legal_entity_id or '',
        'subject_name': contract.get_subject()
    }
    return render_template('contracts/detail.html', contract=contract, edit_mode=True, work_types=work_types, form_data=form_data)

@bp.route('/<int:id>/delete', methods=['POST'])
def delete_contract(id):
    contract = Contract.query.get_or_404(id)
    try:
        document_paths = contract.document_paths.copy()
        additional_file_paths = contract.additional_file_paths.copy()
        db.session.execute(
            contract_documents.delete().where(contract_documents.c.contract_id == id)
        )
        db.session.execute(
            contract_additional_files.delete().where(contract_additional_files.c.contract_id == id)
        )
        db.session.delete(contract)
        db.session.commit()
        for path in document_paths + additional_file_paths:
            try:
                os.remove(os.path.join('uploads', path))
                logging.debug(f"Удален файл: {path}")
            except FileNotFoundError:
                logging.warning(f"Файл не найден для удаления: {path}")
        return redirect(url_for('contracts.list_contracts'))
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in delete_contract: {str(e)}")
        return render_template('contracts/detail.html', contract=contract, edit_mode=False,
                               error=f"Ошибка удаления договора: {str(e)}")

@bp.route('/<int:contract_id>/<path:filename>/<file_type>', methods=['GET'])
def remove_file(contract_id, filename, file_type):
    contract = Contract.query.get_or_404(contract_id)
    try:
        if file_type == 'document':
            db.session.execute(
                contract_documents.delete().where(
                    contract_documents.c.contract_id == contract_id,
                    contract_documents.c.file_path == filename
                )
            )
        elif file_type == 'additional':
            db.session.execute(
                contract_additional_files.delete().where(
                    contract_additional_files.c.contract_id == contract_id,
                    contract_additional_files.c.file_path == filename
                )
            )
        else:
            raise ValueError("Неверный тип файла")
        try:
            os.remove(os.path.join('uploads', filename))
            logging.debug(f"Удален файл: {filename}")
        except FileNotFoundError:
            logging.warning(f"Файл не найден для удаления: {filename}")
        db.session.commit()
        return redirect(url_for('contracts.edit_contract', id=contract_id))
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in remove_file: {str(e)}")
        return render_template('contracts/detail.html', contract=contract, edit_mode=True,
                               error=f"Ошибка удаления файла: {str(e)}",
                               work_types=WorkType.query.all(),
                               form_data={
                                   'number': contract.number,
                                   'contract_date': contract.contract_date.strftime('%Y-%m-%d'),
                                   'address': contract.address,
                                   'object_name': contract.object_name,
                                   'selected_work_types': [str(wt.id) for wt in contract.work_types],
                                   'subject_type': 'physical' if contract.physical_person_id else 'legal' if contract.legal_entity_id else '',
                                   'subject_id': contract.physical_person_id or contract.legal_entity_id or '',
                                   'subject_name': contract.get_subject()
                               })