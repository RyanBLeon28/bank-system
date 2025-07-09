from flask import Flask, render_template, request, redirect, url_for, flash, session
from models.db import db 
from models.user_model import User 
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0131@localhost:5432/bank_db '
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'sua_chave_secreta'

db.init_app(app)

@app.route('/')
def home():
    if 'username' in session:
        return f"Olá, {session['username']}! Você está logado. <a href='/logout'>Sair</a>"
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('home'))
        else:
            flash("Usuário ou senha inválidos!", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Você saiu da conta.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)
