-- MariaDB Docker entrypoint already creates reconciliation_db and grants rec_user.
-- Do not DROP/CREATE the database here; that breaks user grants on first init.

USE reconciliation_db;

/*
The Customer: The one paying.
The Business: The one accepting the payment.
Processor: The tech bridge that encrypts card data and routes it between the parties.
The Card Network: The organization that processes the data (e.g., Visa, Mastercard).
The Bank (Issuing and acquiring): Bank that gives approval and receives funds
*/

-- every transaction originally comes in here 
CREATE TABLE IF NOT EXISTS transactions(
	transaction_id INT PRIMARY KEY AUTO_INCREMENT,
	customer_id INT,
    business_id INT, -- WHERE they're purchasing from
    amount DECIMAL(18, 4),
    received_at DATETIME NOT NULL
    
);

-- In real systems, this would store encrypted card info and format the transaction according to some protocol.
CREATE TABLE IF NOT EXISTS processor_records(
	processor_record_id INT PRIMARY KEY AUTO_INCREMENT,
    transaction_id INT NOT NULL,
	`status` ENUM('Pending', 'Success', 'Failed'),
	received_at DATETIME NOT NULL,
    
    FOREIGN KEY(transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    INDEX idx_processor_tx (transaction_id)
);

-- (VISA, Mastercard, ...) receives request from processor and finds bank to route it to.
CREATE TABLE IF NOT EXISTS card_network_records(
	card_network_record_id INT PRIMARY KEY AUTO_INCREMENT,
    network_name VARCHAR(20),
    transaction_id INT NOT NULL,
	`status` ENUM('Pending', 'Success', 'Failed'),
	received_at DATETIME NOT NULL,
    FOREIGN KEY(transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    INDEX idx_network_tx (transaction_id)
);

-- the bank that receives the funds
CREATE TABLE IF NOT EXISTS bank_transaction_records(
    bank_record_id INT PRIMARY KEY AUTO_INCREMENT,
    transaction_id INT NOT NULL,
    bank_name VARCHAR(50),
    `status` ENUM('Pending', 'Success', 'Failed'),
    received_at DATETIME NOT NULL,
    amount DECIMAL(18,4),
    FOREIGN KEY(transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    INDEX idx_bank_tx (transaction_id)
);

/* GOOD TRANSACTIONS:
same transaction_id exists across all 3 tables,
status progresses: like pending -> Success for all 3 tables,
received_at is ordered from transactions -> Processor -> card_network -> bank
amount never changes (or barely changes)
*/

CREATE TABLE IF NOT EXISTS reconciliation_runs(
	id INT PRIMARY KEY AUTO_INCREMENT,
	start_time DATETIME NOT NULL,
    end_time DATETIME,
    records_checked INT DEFAULT 0,
    num_mismatches INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS reconciliation_results(
	result_id INT PRIMARY KEY AUTO_INCREMENT,
    run_id INT, 
	transaction_id INT NOT NULL,
    `status` ENUM(
		'Match',
		'MissingDownstream', -- transaction exists but didn't make it to the other tables
		'AmountMismatch',
		'StatusMismatch', -- ex: processor = Success, but card_network = Failed
        'OrderMismatch' -- this can happen for ex: because transactions 
						-- start being processed by different tables at the same time
    ) DEFAULT 'Match',
    FOREIGN KEY (run_id) REFERENCES reconciliation_runs(id) ON DELETE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE
);




