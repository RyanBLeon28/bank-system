from models.db import db

class User(db.Model):
    __tablename__ = 'users' 
    cpf = db.Column(db.String, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    create_at = db.Column(db.DateTime)