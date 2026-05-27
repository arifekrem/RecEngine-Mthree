# RecEngine-Mthree

### Directory Structure

```
└── src/
    │
    ├── views/                  # HTTP Routes / Js
    │   ├── api_routes.py       # endpoints to the JavaScript frontend
    │   └── static_routes.py    # Serves the index.html and static files
    │
    ├── controllers/            # Business Logic Coordination
    │   ├── reconciliation.py   # reconciliation algorithm (calls methods from models/discrepancy.py). No Sql logic here
    │   └── simulation.py       # generating good and bad transactions (calls methods from models/transaction_db.py). No Sql logic here
    │
    └── models/                 # MODEL LAYER: Database Interactions
        ├── schema.sql          # MySQL schema
        ├── db_pool.py          # MySQL Connector connection pool setup
        ├── transaction_db.py   # SQL executions for reading/writing transactions
        └── discrepancy_db.py   # SQL executions for recording mismatched entries
```
