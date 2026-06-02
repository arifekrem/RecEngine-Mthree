# RecEngine-Mthree

## Directory Structure

```
RECENGINE-MTHREE/
│
├── docker/                      # Docker configuration
│   ├── Dockerfile               # Flask container build file
│   └── nginx.conf               # Nginx reverse proxy configuration
│
├── grafana/                     # Grafana dashboards & provisioning
│   ├── dashboards/              # Grafana dashboard JSON exports
│   │   └── transactions.json
│   └── provisioning/            # Automatic datasource & dashboard provisioning
│       ├── dashboards/
│       │   └── default.yml
│       └── datasources/
│           └── datasource.yml
│
├── prometheus/                  # Prometheus monitoring configuration
│   └── prometheus.yml
│
├── src/                         # Python backend source code
│   ├── controllers/             # Business Logic Coordination
│   │   ├── reconcile.py         # Categorizes transactions across all tables (match/mismatch)
│   │   └── simulate.py          # Simulates good and bad transactions
│   │
│   ├── models/                  # MODEL LAYER: Database Interactions
│   │   ├── db_pool.py           # MySQL Connector connection pool setup
│   │   ├── discrepancy_db.py    # SQL executions for recording mismatched entries
│   │   ├── schema.sql           # Database schema definition
│   │   └── transaction_db.py    # SQL executions for reading/writing transactions
│   │
│   ├── observability/           # Application metrics & tracking
│   │   └── metrics.py           # Prometheus instrumentations
│   │
│   └── views/                   # HTTP Routes / Endpoints
│       └── api_routes.py        # Flask blueprint and API routes
│
├── static/                      # Frontend static assets
│   ├── css/
│   │   └── style.css            # Custom CSS styling
│   ├── js/
│   │   ├── dashboard.js         # Metrics / analytics scripting
│   │   ├── reconciliation.js    # Reconciliation page scripts
│   │   └── transactions.js      # Transactions view and execution scripts
│   ├── index.html               # Main dashboard UI
│   ├── reconciliation.html      # Reconciliation summary and details UI
│   └── transactions.html        # Transactions list UI
│
├── terraform/                   # AWS Infrastructure as Code
│   ├── main.tf                  # EC2, VPC, Security Groups definitions
│   ├── terraform.tf             # Terraform provider configuration
│   └── variables.tf             # AWS deployment variables
│
├── app.py                       # Main Flask entrypoint
├── docker-compose.yml           # Multi-container setup (Flask, MySQL, Prometheus, Grafana, Nginx)
└── requirements.txt             # Python dependencies
```

---

## Building and Running (Terraform or Docker)

### Terraform Deployment

#### Prerequisites

* **AWS CLI:** Ensure you have the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) installed locally.

#### 1. Generate an SSH Key

If you do not already have an SSH key, generate one:

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa

```

#### 2. Configure AWS Credentials

```bash
aws configure

```

#### 3. Deploy the Infrastructure

```bash
 cd terraform 
 terraform init
 terraform apply

```

#### 4. Monitor Initialization

At this point, the instance is running and visible in your AWS EC2 console. However, it will take approximately 3 minutes for all dependencies to finish installing.

You can monitor the setup progress by SSHing into the instance:

```bash
ssh -i ~/.ssh/id_rsa ec2-user@<instance-public-ip>
tail -f -n 10 /var/log/user-data.log

```

Once finalized, the application will be accessible at: `http://<public-ip>/index` <br>
#### 5. Destroying terraform
```bash
terraform destroy
```

---

### EC2 Instance Configuration and Run Instructions

#### One-Time Setup on EC2 Instance

```bash

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

#### Run Containers

```bash
docker compose up -d --build && docker image prune -f

```

#### Check Running Containers

```bash
docker ps

```

#### Application Access

* **Remote:** [http://your-public-ip/index](https://www.google.com/search?q=http://your-public-ip/index) *(Requires an EC2 inbound security group rule allowing traffic on port 80)*
* **Local:** `curl http://localhost/index`

#### View Logs (HTTP requests + application / DB errors)

```bash
docker compose logs -f flask

```

#### Stop Containers

```bash
docker compose down -v

```

