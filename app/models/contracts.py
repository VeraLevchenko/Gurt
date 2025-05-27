from .. import db
from .work_types import WorkType
from datetime import date

# Таблица ассоциаций
contract_work_types = db.Table(
    'contract_work_types',
    db.Column('contract_id', db.Integer, db.ForeignKey('contracts.id'), primary_key=True),
    db.Column('work_type_id', db.Integer, db.ForeignKey('work_types.id'), primary_key=True)
)

class Contract(db.Model):
    __tablename__ = 'contracts'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), nullable=False, unique=True)
    contract_date = db.Column(db.Date, nullable=False, default=date.today)
    subject = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    work_types = db.relationship('WorkType', secondary=contract_work_types, backref=db.backref('contracts', lazy='dynamic'))

    def __repr__(self):
        return f'<Contract {self.number}>'