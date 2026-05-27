# RecEngine-Mthree

### Directory Structure

```
└── src/
    │
    ├── views/                  # HTTP Routes / Js
    │   ├── __init__.py
    │   ├── api_routes.py       # endpoints to the JavaScript frontend
    │   └── static_routes.py    # Serves the index.html and static files
    │
    ├── controllers/            # Business Logic Coordination
    │   ├── __init__.py
    │   ├── reconciliation.py   # reconciliation algorithm (calls methods from models/discrepancy.py). No Sql logic here
    │   └── simulation.py       # generating good and bad transactions (calls methods from models/transaction_db.py). No Sql logic here
    │
    └── models/                 # MODEL LAYER: Database Interactions
        ├── __init__.py
        ├── db_pool.py          # MySQL Connector connection pool setup
        ├── transaction_db.py   # SQL executions for reading/writing transactions
        └── discrepancy_db.py   # SQL executions for recording mismatched entries
```

### Ec2 instance configuration, and how to run (docker later)

```
# Update python to 3.13 and install pip
sudo dnf update -y
sudo dnf install python3.13 python3.13-pip python3.13-devel -y
sudo dnf install python3-pip -y

# Install flask and mysql-connector 
pip3 install Flask
pip3 install mysql-connector-python

# mariadb is basically the same as mySql
sudo dnf install -y mariadb105-server
sudo systemctl start mariadb
sudo systemctl enable mariadb
sudo mysql -u root

CREATE DATABASE reconciliation_db;
CREATE USER 'rec_user'@'127.0.0.1' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON reconciliation_db.* TO 'rec_user'@'127.0.0.1';
FLUSH PRIVILEGES;
EXIT;

mysql -u rec_user -p -h 127.0.0.1 reconciliation_db < schema.sql 
password >> 'password'

cd python3 RecEngine-Mthree/app.py

>>> * Running on all addresses (0.0.0.0)
>>> * Running on http://127.0.0.1:5000
>>> * Running on http://172.31.32.120:5000

```

