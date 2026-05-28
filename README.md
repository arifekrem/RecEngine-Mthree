# RecEngine-Mthree

### Directory Structure

```
RECENGINE-MTHREE/
│
├── src/
│   ├── controllers/             # Business Logic Coordination
│   │   ├── reconcile.py         # categorizes transactions across all tables (match/mismatch)
│   │   └── simulate.py          # simulates good and bad transactions
│   │
│   ├── models/                  # MODEL LAYER: Database Interactions
│   │   ├── db_pool.py           # MySQL Connector connection pool setup
│   │   ├── discrepancy_db.py    # SQL executions for recording mismatched entries
│   │   ├── schema.sql
│   │   └── transaction_db.py    # SQL executions for reading/writing transactions
│   │
│   ├── views/                   # HTTP Routes / Js
│   │   ├── api_routes.py
│   │   ├── index.html
│   │   ├── reconciliation.html
│   │   ├── transactions.html
│
├── static/
│   ├── js/
│   ├── app.js
│   ├── index.html
│   └── style.css
├── app.py                      # Entry point
├── Project-Description.md
├── requirements.txt
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

mysql -u rec_user -p -h 127.0.0.1 reconciliation_db < /path/to/schema.sql 
password >> 'password'

python3 RecEngine-Mthree/app.py

>>> * Running on all addresses (0.0.0.0)
>>> * Running on http://127.0.0.1:5000
>>> * Running on http://172.31.32.120:5000

# see routes in RecEngine-Mthree/src/views/api_routes.py
```

