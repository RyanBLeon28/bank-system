import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models.db import db 
from models.user_model import User 
from models.account_model import Account 
from models.transactions_model import Transaction
from decimal import Decimal

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost:5432/bank_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'sua_chave_secreta'

db.init_app(app)

@app.route('/')
def home():
    if 'cpf' in session:
        user = User.query.filter_by(cpf=session['cpf']).first()
        if user:
            account = Account.query.filter_by(cpf=user.cpf).first()
            transactions = []
            if account:
                transactions = Transaction.query.filter(
                    (Transaction.source_account == account.id) | (Transaction.target_account == account.id)
                ).order_by(Transaction.created_at.desc()).all()

            return render_template('index.html', user=user, account=account, transactions=transactions)
        else:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for('logout'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf = request.form['cpf']
        password = request.form['password']

        user = User.query.filter_by(cpf=cpf).first()

        if user and user.password_hash == password:
            session['cpf'] = user.cpf
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('home'))
        else:
            flash("Usuário ou senha inválidos!", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'cpf' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(cpf=session['cpf']).first()
    account = Account.query.filter_by(cpf=user.cpf).first()

    if request.method == 'POST':
        target_id = request.form['target']
        amount = Decimal(request.form['amount'])

        # Check balance
        if amount <= 0:
            flash("O valor da transferência deve ser maior que zero.", "danger")
        elif amount > float(account.balance):
            flash("Saldo insuficiente.", "danger")
        else:
            target_account = Account.query.filter_by(id=target_id).first()
            if not target_account:
                flash("Conta de destino não encontrada.", "danger")
            elif target_account.id == account.id:
                flash("Não é possível transferir para a mesma conta.", "danger")
            else:
                # Update balance
                account.balance -= amount
                target_account.balance += amount

                # Create transaction
                transaction = Transaction(
                    source_account=account.id,
                    target_account=target_account.id,
                    amount=amount,
                    type='transfer'
                )

                db.session.add(transaction)
                db.session.commit()

                flash("Transferência realizada com sucesso!", "success")
                return redirect(url_for('home'))

    return render_template('transfer.html', user=user, account=account)


@app.route('/logout')
def logout():
    session.pop('cpf', None)
    flash("Você saiu da conta.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)
