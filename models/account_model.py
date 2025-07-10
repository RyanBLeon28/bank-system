from models.db import db

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.String, primary_key=True)
    cpf = db.Column(db.String, db.ForeignKey('users.cpf'))
    balance = db.Column(db.Numeric(10, 2), default=0.00)
    create_at = db.Column(db.DateTime, server_default=db.func.now())