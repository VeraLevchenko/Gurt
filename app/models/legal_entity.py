from .. import db

class LegalEntity(db.Model):
    __tablename__ = 'legal_entities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    inn = db.Column(db.String(50), nullable=False, unique=True)
    legal_address = db.Column(db.String(255), nullable=False)
    director_full_name = db.Column(db.String(255), nullable=False)
    payment_details = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<LegalEntity {self.name}>'