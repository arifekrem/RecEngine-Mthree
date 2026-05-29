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
│   │   └── api_routes.py
│   │
│   └── observability/           # Prometheus metrics for transaction monitoring
│       └── metrics.py
│
├── prometheus/
│   └── prometheus.yml           # Scrape config (targets flask:5000/metrics)
├── grafana/
│   ├── provisioning/            # Auto-configured Prometheus datasource
│   └── dashboards/              # RecEngine Transactions dashboard
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

### EC2 instance configuration and run instructions

### One-time setup on EC2 instance

```bash
# Install MariaDB
sudo dnf install -y mariadb105-server
sudo systemctl start mariadb
sudo systemctl enable mariadb
sudo mysql -u root

# Install Docker
sudo dnf install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m) -o /usr/libexec/docker/cli-plugins/docker-compose
sudo chmod +x /usr/libexec/docker/cli-plugins/docker-compose
docker compose version

# Install buildx (required; missing causes errors)
mkdir -p ~/.docker/cli-plugins
BUILDX_VERSION=$(curl -s https://api.github.com/repos/docker/buildx/releases/latest | grep -oP '"tag_name": "\K[^"]+')
curl -L https://github.com/docker/buildx/releases/download/${BUILDX_VERSION}/buildx-${BUILDX_VERSION}.linux-amd64 -o ~/.docker/cli-plugins/docker-buildx
chmod +x ~/.docker/cli-plugins/docker-buildx
docker buildx version
```

### Run containers

```bash
docker compose up -d --build && docker image prune -f
```

### Check running containers

```bash
docker ps
```

Access:

* [http://your-public-ip/index](http://your-public-ip/index) (requires EC2 inbound rule on port 80)
* or locally: `curl http://localhost/index`

### Observability (Prometheus + Grafana)

Prometheus and Grafana run in the same Docker Compose stack and monitor transaction activity via Flask `/metrics`.

| Service | URL | Notes |
|---------|-----|-------|
| Grafana | [http://localhost:3000](http://localhost:3000) | login `admin` / `admin` |
| Prometheus | [http://localhost:9090](http://localhost:9090) | scrapes `flask:5000/metrics` every 15s |
| Metrics | `http://flask:5000/metrics` (internal) | counters + DB gauges |

Open Grafana → **Dashboards → RecEngine → RecEngine Transactions** after generating data (simulation, manual transactions, or reconciliation runs).

Metrics exposed:

* `recengine_transactions_created_total` / `_deleted_total`
* `recengine_transactions_in_database` (live row count)
* `recengine_pipeline_failures_total` by stage
* `recengine_simulation_transactions_total` (good vs chaos)
* `recengine_reconciliation_results_by_status`
* `recengine_reconciliation_last_mismatches` / `_last_records_checked`

On EC2, open inbound rules for ports **3000** (Grafana) and **9090** (Prometheus) if you need external access.

### Logs (HTTP requests + application / DB errors)

```bash
docker compose logs -f flask
```

### Stop containers

```bash
docker compose down -v
```



