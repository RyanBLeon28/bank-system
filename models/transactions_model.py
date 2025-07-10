from models.db import db

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    source_account = db.Column(db.String, db.ForeignKey('accounts.id'))
    target_account = db.Column(db.String, db.ForeignKey('accounts.id'))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.String, nullable=False)  # deposit, withdraw, transfer
    created_at = db.Column(db.DateTime, server_default=db.func.now())