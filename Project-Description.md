### 1. THE PROJECT CONCEPT & BUSINESS DOMAIN
We are building an automated financial reconciliation and observability platform. 

In corporate banking, financial data consistency across independent ledgers is a mission-critical constraint. Every day, our system must ingest and validate two distinct high-throughput streams of transactional data:
- Internal Ledgers (records of transaction attempts logged directly inside our bank's database).
- External Clearing Files (settlement transaction records provided to us at the end of the day by networks like Visa, MasterCard, or SWIFT).

Our application's core logic is to run an asynchronous batch matching algorithm that cross-references these two data streams based on unique transaction reference keys, exact currency amounts, and close timestamp windows. 
- A "Match" occurs when internal and external records perfectly align.
- An "Anomaly" or "Break" occurs when a transaction exists on one side but is completely missing from the other (orphans), or if there is an amount/currency discrepancy. These must be caught, flagged, and written to an audit log for review.

---

### 2. THE SRE, MONITORING & USER INTERFACE LAYER
This project is an enterprise-grade Site Reliability Engineering (SRE) showcase. The user interface is an Operator’s Control Panel built directly into our app using zero-build frontend tools: Flask Jinja2 native templates, Bootstrap 5 (via CDN) for clean grid layouts, and Alpine.js (via CDN) for asynchronous, non-page-refreshing click events. 

This frontend will feature a "Happy Path" button to run standard clean reconciliation loops and a "Chaos Injection" button to intentionally trigger database mismatches.

The platform is hooked directly into an advanced telemetry pipeline. The database must be structured to seamlessly feed our SRE monitoring stack (Prometheus & Grafana) so we can map low-level database constraints to business-level Service Level Objectives (SLOs) and track our Data Integrity Error Budget in real-time.

---

### 3. THE COMPLETE TECH STACK
Our environment is fully locked in and will utilize the following tools:
- Frontend Control Panel: Flask Jinja2 Templates, Bootstrap 5, and Alpine.js.
- Backend Core: Python 3.11+ using the Flask framework.
- Database: MySQL 8.0 (ACID-compliant relational database engine).
- Web Routing & Proxy: Nginx (Handling edge routing and secure reverse proxy mappings).
- Container Execution: Docker & Docker Compose (Containerizing the microservices into an isolated bridge network).
- Provisioning Infrastructure: Terraform (Automating hardware configurations via Code).
- Cloud Target: AWS EC2 (A single optimized t3.medium instance hosting our production deployment).
- Observability Architecture: Prometheus (Scraping live system metrics) and Grafana (Processing PromQL for monitoring dashboards).

---

### 4. PROJECT TIMELINE & VELOCITY CONSTRAINTS
- Project Kickoff: May 23, 2026
- Presentation/Go-Live Date: Wednesday, June 3, 2026
- Total Duration: 11 Days



Customer: The one paying.

The Business: The one accepting the payment.

Processor: encrypts card data and routes it between the parties. (I didn't bother with card info and all that for now)

The Card Network: The organization that processes the data (e.g., Visa, Mastercard).

The Bank (Issuing and acquiring): Bank that gives approval and receives funds
 
customer buys something --(tables)--> transactions -> processor_records -> card_network_records -> bank_transaction_records
 
 and for good transactions:
 
same transaction_id exists across all 3 tables,

status progression across tables: pending -> Success for all 3 tables,

received_at is ordered from transactions -> Processor -> card_network -> bank

amount never changes (or barely changes)
 Also this is what I was thinking our project should do overall:
 
user requests /simulate/run :
    backend generates good and bad transactions which are put into db
user requests /simulate/reconcile:
    processes all tables (join by transaction_id) and does something when faulty transaction, or just counts them and writes them into reconciliation results