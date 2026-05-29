# RecEngine-Mthree

## Directory Structure

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

Once finalized, the application will be accessible at: `http://<public-ip>/index`

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

