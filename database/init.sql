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

INSERT INTO accounts (id, cpf, balance) VALUES
('ACC001', '123.234.456-78', 1500.00),  
('ACC002', '123.234.456-00', 2200.50),  
('ACC003', '123.234.456-01', 320.75),   
('ACC004', '123.234.456-02', 5000.00),  
('ACC005', '123.234.456-03', 870.90);  

INSERT INTO transactions (target_account, amount, type) VALUES
('ACC001', 500.00, 'deposit'),
('ACC002', 700.00, 'deposit'),
('ACC003', 100.00, 'deposit');

INSERT INTO transactions (source_account, amount, type) VALUES
('ACC004', 200.00, 'withdraw'),
('ACC005', 150.00, 'withdraw');

INSERT INTO transactions (source_account, target_account, amount, type) VALUES
('ACC001', 'ACC003', 120.00, 'transfer'),
('ACC002', 'ACC005', 300.00, 'transfer'),
('ACC004', 'ACC001', 1000.00, 'transfer');