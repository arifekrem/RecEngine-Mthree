-- Run once on existing databases created before Pending was added to reconciliation_results.
USE reconciliation_db;

ALTER TABLE reconciliation_results
MODIFY COLUMN status ENUM(
    'Match',
    'Pending',
    'MissingDownstream',
    'AmountMismatch',
    'StatusMismatch',
    'OrderMismatch'
) DEFAULT 'Match';
