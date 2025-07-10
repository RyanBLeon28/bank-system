

Executar script SQL no SGBD Postgres

psql -U postgres -d bank_system -f database/init.sql


Acessar PostgreSQL dentro da Database
sudo -u postgres psql -d bank_system



python3 -m venv venv
source venv/bin/activate 
pip install flask