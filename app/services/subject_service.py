from __future__ import annotations

from typing import Sequence

from sqlalchemy.exc import IntegrityError

from .. import db
from ..models.physical_person import PhysicalPerson
from ..models.legal_entity import LegalEntity
from ..models.contracts import Contract


class SubjectService:
    """Операции над физическими и юридическими лицами."""

    # --------------- Чтение ------------------------------------------------

    @staticmethod
    def list_physical() -> Sequence[PhysicalPerson]:
        return PhysicalPerson.query.all()

    @staticmethod
    def list_legal() -> Sequence[LegalEntity]:
        return LegalEntity.query.all()

    @staticmethod
    def search_physical(query: str) -> Sequence[PhysicalPerson]:
        return PhysicalPerson.query.filter(
            (PhysicalPerson.full_name.ilike(f"%{query}%"))
            | (PhysicalPerson.passport.ilike(f"%{query}%"))
        ).all()

    @staticmethod
    def search_legal(query: str) -> Sequence[LegalEntity]:
        return LegalEntity.query.filter(
            (LegalEntity.name.ilike(f"%{query}%"))
            | (LegalEntity.inn.ilike(f"%{query}%"))
        ).all()

    @staticmethod
    def get(subject_type: str, subject_id: int):
        if subject_type == "physical":
            return PhysicalPerson.query.get_or_404(subject_id)
        if subject_type == "legal":
            return LegalEntity.query.get_or_404(subject_id)
        raise ValueError("Неверный тип субъекта")

    # --------------- Создание ---------------------------------------------

    @staticmethod
    def create_physical(data) -> PhysicalPerson:
        person = PhysicalPerson(**data)
        db.session.add(person)
        SubjectService._commit()
        return person

    @staticmethod
    def create_legal(data) -> LegalEntity:
        entity = LegalEntity(**data)
        db.session.add(entity)
        SubjectService._commit()
        return entity

    # --------------- Обновление -------------------------------------------

    @staticmethod
    def update(subject, data) -> None:
        for field, value in data.items():
            setattr(subject, field, value)
        SubjectService._commit()

    # --------------- Удаление ---------------------------------------------

    @staticmethod
    def delete(subject_type: str, subject_id: int) -> None:
        if subject_type == "physical":
            linked = Contract.query.filter_by(physical_person_id=subject_id).first()
        else:
            linked = Contract.query.filter_by(legal_entity_id=subject_id).first()
        if linked:
            raise ValueError("Нельзя удалить субъект, связанный с договором")

        subj = SubjectService.get(subject_type, subject_id)
        db.session.delete(subj)
        SubjectService._commit()

    # --------------- Внутреннее -------------------------------------------

    @staticmethod
    def _commit():
        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("Такое лицо уже существует") from exc
