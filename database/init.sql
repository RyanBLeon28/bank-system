-- User table
CREATE TABLE IF NOT EXISTS users (
    cpf VARCHAR PRIMARY KEY,
    username VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL,
    create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Account table
CREATE TABLE IF NOT EXISTS accounts (
    id VARCHAR PRIMARY KEY,
    cpf VARCHAR REFERENCES users(cpf),
    balance DECIMAL(10,2) DEFAULT 0.00,
    create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    source_account VARCHAR REFERENCES accounts(id),
    target_account VARCHAR REFERENCES accounts(id),
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    type VARCHAR NOT NULL CHECK (type IN ('deposit', 'withdraw', 'transfer')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO users
(cpf,username,password_hash)
VALUES
('123.234.456-78','Pedro','pedroSenha');

INSERT INTO users
(cpf,username,password_hash)
VALUES
('123.234.456-00','Valerio','valerioSenha');

INSERT INTO users
(cpf,username,password_hash)
VALUES
('123.234.456-01','Gabriel','gabrielSenha');

INSERT INTO users
(cpf,username,password_hash)
VALUES
('123.234.456-02','Joao','joaoSenha');

INSERT INTO users
(cpf,username,password_hash)
VALUES
('123.234.456-03','Roberto','robertoSenha');