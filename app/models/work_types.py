from .. import db

class WorkType(db.Model):
    __tablename__ = 'work_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)  # Изменено с 100 на 255
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<WorkType {self.name}>'