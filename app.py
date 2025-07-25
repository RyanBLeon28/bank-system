import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models.db import db 
from models.user_model import User 
from models.account_model import Account 
from models.transactions_model import Transaction
from decimal import Decimal
from sqlalchemy import func
from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies, unset_jwt_cookies, jwt_required, get_jwt_identity
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost:5432/bank_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'sua_chave_secreta'

app.config['JWT_SECRET_KEY'] = 'sua_chave_super_secreta'  # troque isso em produção!
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # True para HTTPS
app.config['JWT_COOKIE_CSRF_PROTECT'] = False 
jwt = JWTManager(app)

db.init_app(app)

@app.route('/')
@jwt_required(optional=True)
def home():
    cpf = get_jwt_identity()
    print("CPF do token:", get_jwt_identity())
    if not cpf:
        return redirect(url_for('login'))
    user = User.query.filter_by(cpf=cpf).first()
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf = request.form['cpf']
        password = request.form['password']

        user = User.query.filter_by(cpf=cpf).first()

        if user and user.password_hash == password:
            access_token = create_access_token(identity=cpf, expires_delta=timedelta(hours=1))
            resp = redirect(url_for('home'))
            set_access_cookies(resp, access_token)
            flash("Login realizado com sucesso!", "success")
            return resp
        else:
            flash("Usuário ou senha inválidos!", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        cpf = request.form['cpf']
        password = request.form['password']
        confirm_password = request.form['confirm_password'] 
        
        if password != confirm_password:
            flash("As senhas não coincidem!", "danger")
            return redirect(url_for('register'))

        # Check if CPF already exists
        existing_cpf = User.query.filter_by(cpf=cpf).first()

        if existing_cpf:
            flash("CPF já cadastrado. Por favor, use um CPF diferente.", "danger")
            return redirect(url_for('register'))

        # Create a new user
        new_user = User(username=username, cpf=cpf, password_hash=password)
        db.session.add(new_user)
        db.session.commit()

        accounts = db.session.query(func.count(Account.id)).scalar()
        new_account_id = f"ACC{(accounts+1):03d}"

        existing_account = Account.query.filter_by(id=new_account_id).first()
        if existing_account:
            flash("Erro ao gerar ID da conta. Tente novamente.", "danger")
            return redirect(url_for('some_error_page'))

        new_account = Account(id=new_account_id, cpf=cpf, balance=0.00)

        try:
            db.session.add(new_account)
            db.session.commit()
            flash(f"Conta criada com sucesso!", "success")
            return redirect(url_for('login')) 
        except Exception as e:
            db.session.rollback() # Rollback in case of error
            flash(f"Erro ao criar conta: {str(e)}", "danger")
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/transfer', methods=['GET', 'POST'])
@jwt_required()
def transfer():
    cpf = get_jwt_identity()

    user = User.query.filter_by(cpf=cpf).first()
    account = Account.query.filter_by(cpf=user.cpf).first()

    if request.method == 'POST':
        target_id = request.form['target']
        amount = Decimal(request.form['amount'])
        password = request.form['password']

        # Validação da senha
        if user.password_hash != password:
            flash("Senha incorreta. Confirme sua senha para transferir.", "danger")
            return redirect(url_for('transfer'))

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
                # return redirect(url_for('home'))
                return render_template("transfer_success.html")

    return render_template('transfer.html', user=user, account=account)


@app.route('/extrato')
@jwt_required()
def extrato():
    cpf = get_jwt_identity()
    user = User.query.filter_by(cpf=cpf).first()
    account = Account.query.filter_by(cpf=cpf).first()
    transactions = []
    if account:
        transactions = Transaction.query.filter(
            (Transaction.source_account == account.id) | (Transaction.target_account == account.id)
        ).order_by(Transaction.created_at.desc()).all()
    return render_template('extrato.html', user=user, account=account, transactions=transactions)

@app.route('/dados_conta')
@jwt_required()
def dados_conta():
    cpf = get_jwt_identity()
    user = User.query.filter_by(cpf=cpf).first()
    account = Account.query.filter_by(cpf=cpf).first()
    return render_template('dados_conta.html', user=user, account=account)

@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    resp = redirect(url_for('login'))
    unset_jwt_cookies(resp)
    flash("Você saiu da conta.", "info")
    return resp

@app.route('/delete_account', methods=['POST'])
@jwt_required()
def delete_account():
    cpf = get_jwt_identity()
    user = User.query.filter_by(cpf=cpf).first()
    account = Account.query.filter_by(cpf=cpf).first()

    if user and account:
        try:
            db.session.delete(account)
            db.session.delete(user)
            db.session.commit()

            resp = redirect(url_for('login'))
            unset_jwt_cookies(resp)
            flash("Conta excluída com sucesso.", "success")
            return resp
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao excluir conta: {str(e)}", "danger")
            return redirect(url_for('dados_conta'))

    flash("Conta não encontrada.", "danger")
    return redirect(url_for('dados_conta'))
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)
