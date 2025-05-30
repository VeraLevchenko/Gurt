from .. import db

class WorkType(db.Model):
    __tablename__ = 'work_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    unit = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    price_with_vat = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<WorkType {self.name}>'