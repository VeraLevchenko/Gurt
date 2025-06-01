from .. import db

class PhysicalPerson(db.Model):
    __tablename__ = 'physical_persons'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    passport = db.Column(db.String(255), nullable=False, unique=True)
    address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<PhysicalPerson {self.full_name}>'