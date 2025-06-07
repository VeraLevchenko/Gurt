from .. import db
from .work_types import WorkType
from datetime import date

# Таблица ассоциаций для типов работ
contract_work_types = db.Table(
    'contract_work_types',
    db.Column('contract_id', db.Integer, db.ForeignKey('contracts.id'), primary_key=True),
    db.Column('work_type_id', db.Integer, db.ForeignKey('work_types.id'), primary_key=True)
)

# Таблица для вложений документов (договор, смета, техзадание, акт приемки)
contract_documents = db.Table(
    'contract_documents',
    db.Column('contract_id', db.Integer, db.ForeignKey('contracts.id'), primary_key=True),
    db.Column('file_path', db.String(255), nullable=False)
)

# Таблица для дополнительных вложений
contract_additional_files = db.Table(
    'contract_additional_files',
    db.Column('id', db.Integer, primary_key=True, autoincrement=True),
    db.Column('contract_id', db.Integer, db.ForeignKey('contracts.id'), nullable=False),
    db.Column('file_path', db.String(255), nullable=False)
)

class Contract(db.Model):
    __tablename__ = 'contracts'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), nullable=False, unique=True)
    contract_date = db.Column(db.Date, nullable=False, default=date.today)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    object_name = db.Column(db.String(255), nullable=False)  # Новое поле "объект"
    physical_person_id = db.Column(db.Integer, db.ForeignKey('physical_persons.id'), nullable=True)
    legal_entity_id = db.Column(db.Integer, db.ForeignKey('legal_entities.id'), nullable=True)
    work_types = db.relationship('WorkType', secondary=contract_work_types, backref=db.backref('contracts', lazy='dynamic'))
    
    # Связь с физическим лицом
    physical_person = db.relationship('PhysicalPerson', backref='contracts')
    # Связь с юридическим лицом
    legal_entity = db.relationship('LegalEntity', backref='contracts')

    @property
    def document_paths(self):
        """Возвращает список путей к документам."""
        result = db.session.execute(
            db.select(contract_documents.c.file_path).where(contract_documents.c.contract_id == self.id)
        ).scalars().all()
        return result

    @property
    def additional_file_paths(self):
        """Возвращает список путей к дополнительным файлам."""
        result = db.session.execute(
            db.select(contract_additional_files.c.file_path).where(contract_additional_files.c.contract_id == self.id)
        ).scalars().all()
        return result

    def get_subject(self):
        """Возвращает строковое представление субъекта."""
        if self.physical_person:
            return self.physical_person.full_name
        elif self.legal_entity:
            return self.legal_entity.name
        return "Не указан"

    def __repr__(self):
        return f'<Contract {self.number}>'