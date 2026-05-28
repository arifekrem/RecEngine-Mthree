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
# install mariadb in container
sudo dnf install -y mariadb105-server
sudo systemctl start mariadb
sudo systemctl enable mariadb
sudo mysql -u root

# install docker
sudo dnf install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker

# install docker compose
sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m) -o /usr/libexec/docker/cli-plugins/docker-compose
sudo chmod +x /usr/libexec/docker/cli-plugins/docker-compose
docker compose version

# buildx version for docker (if you dont do that = error)
mkdir -p ~/.docker/cli-plugins
BUILDX_VERSION=$(curl -s https://api.github.com/repos/docker/buildx/releases/latest | grep -oP '"tag_name": "\K[^"]+')
curl -L https://github.com/docker/buildx/releases/download/${BUILDX_VERSION}/buildx-${BUILDX_VERSION}.linux-amd64   -o ~/.docker/cli-plugins/docker-buildx
chmod +x ~/.docker/cli-plugins/docker-buildx
docker buildx version

docker compose up -d --build && docker image prune -f
docker compose down -v

# check containers
docker ps

# You can visit http://your-public-ip/index (need to allow inbound rules to port 80 in ec2 console)
# Or curl http://localhost/index in ec2 terminal to check locally
```

