from .. import db
from datetime import date

class Contract(db.Model):
    __tablename__ = 'contracts'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), nullable=False, unique=True)
    contract_date = db.Column(db.Date, nullable=False, default=date.today)
    subject = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    work_description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Contract {self.number}>'