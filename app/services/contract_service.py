from __future__ import annotations

import io
import logging
import os
import re
from datetime import datetime, date
from typing import List, Sequence
from uuid import uuid4

from flask import current_app, send_file
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from werkzeug.utils import secure_filename

from .. import db
from ..models.contracts import Contract, contract_documents, contract_additional_files
from ..models.work_types import WorkType
from ..models.physical_person import PhysicalPerson
from ..models.legal_entity import LegalEntity

_log = logging.getLogger(__name__)


class ContractService:
    """Бизнес-логика, связанная с договорами."""

    ALLOWED_EXTENSIONS = {".pdf", ".docx"}
    NUMBER_RE = re.compile(r"^08-0/\d+$")

    # -----------------------------------------------------------------
    # ────────────────  У Т И Л И Т Ы  ─────────────────
    # -----------------------------------------------------------------
    @classmethod
    def validate_number(cls, number: str) -> None:
        if not cls.NUMBER_RE.match(number):
            raise ValueError("Номер должен быть в формате 08-0/XXXXX")

    @staticmethod
    def allowed_file(filename: str) -> bool:
        return os.path.splitext(filename)[1].lower() in ContractService.ALLOWED_EXTENSIONS

    @staticmethod
    def unique_filename(original: str) -> str:
        ext = os.path.splitext(original)[1].lower()
        return secure_filename(f"{uuid4()}{ext}")

    # -----------------------------------------------------------------
    # ────────────────  Ч Т Е Н И Е  ─────────────────
    # -----------------------------------------------------------------
    @classmethod
    def list(cls) -> Sequence[Contract]:
        return Contract.query.all()

    # -----------------------------------------------------------------
    # ────────────────  С О З Д А Н И Е  ─────────────────
    # -----------------------------------------------------------------
    @classmethod
    def create_from_request(cls, form, files) -> Contract:
        number = form["number"].strip()
        cls.validate_number(number)

        if Contract.query.filter_by(number=number).first():
            raise ValueError(f"Номер договора «{number}» уже существует")

        object_name = form["object_name"].strip() or None
        if not object_name:
            raise ValueError("Поле «Объект» не может быть пустым")

        work_type_ids = form.getlist("work_description")
        if not work_type_ids:
            raise ValueError("Не выбран ни один вид работ")
        work_types = WorkType.query.filter(WorkType.id.in_(work_type_ids)).all()

        subject = cls._get_subject(form.get("subject_type"), form.get("subject_id"))

        doc_paths = cls._save_attachments(files.getlist("documents"), max_files=4)
        add_paths = cls._save_attachments(files.getlist("additional_files"), max_files=10)

        contract = Contract(
            number=number,
            contract_date=datetime.strptime(form["contract_date"], "%Y-%m-%d").date(),
            price=sum(w.price for w in work_types),
            address=form["address"].strip(),
            object_name=object_name,
            work_types=work_types,
        )
        if isinstance(subject, PhysicalPerson):
            contract.physical_person_id = subject.id
        else:
            contract.legal_entity_id = subject.id

        db.session.add(contract)
        db.session.flush()  # нужен id

        cls._attach_files(contract.id, doc_paths, add_paths)
        db.session.commit()
        _log.info("Создан договор %s", contract.number)
        return contract

    # -----------------------------------------------------------------
    # ────────────────  О Б Н О В Л Е Н И Е  ─────────────────
    # -----------------------------------------------------------------
    @classmethod
    def update_from_request(cls, contract: Contract, form, files) -> Contract:
        cls.validate_number(form["number"])
        contract.number = form["number"]
        contract.object_name = form["object_name"].strip()
        contract.contract_date = datetime.strptime(form["contract_date"], "%Y-%m-%d").date()
        contract.address = form["address"].strip()

        work_type_ids = form.getlist("work_description")
        if not work_type_ids:
            raise ValueError("Не выбран ни один вид работ")
        contract.work_types = WorkType.query.filter(WorkType.id.in_(work_type_ids)).all()
        contract.price = sum(w.price for w in contract.work_types)

        subject = cls._get_subject(form.get("subject_type"), form.get("subject_id"))
        contract.physical_person_id = contract.legal_entity_id = None
        if isinstance(subject, PhysicalPerson):
            contract.physical_person_id = subject.id
        else:
            contract.legal_entity_id = subject.id

        cls._replace_attachments(contract.id, files.getlist("documents"), files.getlist("additional_files"))
        db.session.commit()
        _log.info("Договор %s обновлён", contract.number)
        return contract

    # -----------------------------------------------------------------
    # ────────────────  У Д А Л Е Н И Е  ─────────────────
    # -----------------------------------------------------------------
    @classmethod
    def delete(cls, contract: Contract) -> None:
        upload_dir = current_app.config.get("UPLOAD_FOLDER", "uploads")

        # сохраним, чтобы потом убрать файлы с диска
        docs = contract.document_paths.copy()
        adds = contract.additional_file_paths.copy()

        db.session.execute(contract_documents.delete().where(contract_documents.c.contract_id == contract.id))
        db.session.execute(contract_additional_files.delete().where(contract_additional_files.c.contract_id == contract.id))
        db.session.delete(contract)
        db.session.commit()

        for path in (*docs, *adds):
            try:
                os.remove(os.path.join(upload_dir, path))
            except FileNotFoundError:
                _log.debug("Файл %s не найден при удалении", path)

    # -----------------------------------------------------------------
    # ────────────────  Э К С П О Р Т   X L S X  ─────────────────
    # -----------------------------------------------------------------
    @classmethod
    def export_excel(cls):
        wb = Workbook()
        ws = wb.active
        ws.title = "Договоры"
        headers = ["Номер", "Дата", "Субъект", "Цена", "Адрес", "Объект", "Виды работ"]
        for col, h in enumerate(headers, 1):
            ws[f"{get_column_letter(col)}1"] = h

        for row, c in enumerate(cls.list(), 2):
            ws[f"A{row}"] = c.number
            ws[f"B{row}"] = c.contract_date.strftime("%Y-%m-%d")
            ws[f"C{row}"] = c.get_subject()
            ws[f"D{row}"] = c.price
            ws[f"E{row}"] = c.address
            ws[f"F{row}"] = c.object_name
            ws[f"G{row}"] = "; ".join(f"{w.name} ({w.price}₽)" for w in c.work_types)

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return send_file(
            buf,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="contracts.xlsx",
        )

    # -----------------------------------------------------------------
    # ────────────────  В Н У Т Р Е Н Н Е Е  ─────────────────
    # -----------------------------------------------------------------
    @staticmethod
    def _get_subject(subject_type: str, subject_id):
        if subject_type == "physical":
            return PhysicalPerson.query.get_or_404(subject_id)
        if subject_type == "legal":
            return LegalEntity.query.get_or_404(subject_id)
        raise ValueError("Неверный тип субъекта")

    @classmethod
    def _save_attachments(cls, files, *, max_files: int) -> List[str]:
        """
        Сохраняет файлы и возвращает **basename** каждого файла для хранения в БД.
        """
        if len(files) > max_files:
            raise ValueError(f"Можно загрузить не более {max_files} файлов")

        upload_dir = current_app.config.get("UPLOAD_FOLDER", "uploads")
        paths: List[str] = []

        for f in files:
            if not f or not f.filename:
                continue
            if not cls.allowed_file(f.filename):
                raise ValueError("Допустимы только PDF и DOCX")

            name = cls.unique_filename(f.filename)  # uuid.pdf
            f.save(os.path.join(upload_dir, name))
            paths.append(name)

        return paths

    @classmethod
    def _attach_files(cls, contract_id: int, docs: List[str], adds: List[str]) -> None:
        for p in docs:
            db.session.execute(contract_documents.insert().values(contract_id=contract_id, file_path=p))
        for p in adds:
            db.session.execute(contract_additional_files.insert().values(contract_id=contract_id, file_path=p))

    @classmethod
    def _replace_attachments(cls, contract_id: int, new_docs, new_adds) -> None:
        upload_dir = current_app.config.get("UPLOAD_FOLDER", "uploads")

        contract = Contract.query.get(contract_id)
        old_docs = set(contract.document_paths)
        old_adds = set(contract.additional_file_paths)

        docs = old_docs.union(cls._save_attachments(new_docs, max_files=4))
        adds = old_adds.union(cls._save_attachments(new_adds, max_files=10))

        db.session.execute(contract_documents.delete().where(contract_documents.c.contract_id == contract_id))
        db.session.execute(contract_additional_files.delete().where(contract_additional_files.c.contract_id == contract_id))
        cls._attach_files(contract_id, list(docs), list(adds))

        # удалить физически ненужные файлы
        for p in (old_docs | old_adds) - (docs | adds):
            try:
                os.remove(os.path.join(upload_dir, p))
            except FileNotFoundError:
                _log.debug("Файл %s не найден при чистке", p)
