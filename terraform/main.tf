provider "aws" {
    region = var.aws_region # This uses user's region automatically

}

data "aws_ami" "amazon_linux_2023" {
  most_recent = true

  filter {
    name = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  owners = ["137112412989"] # Amazon
}

resource "aws_security_group" "app_sg" {
  name        = "app-sg"
  description = "Allow HTTP and SSH"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] 
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_key_pair" "deployer" {
  key_name   = "learning-terraform-key"
  public_key = file("~/.ssh/id_rsa.pub") 
}


resource "aws_instance" "app" {
    ami = data.aws_ami.amazon_linux_2023.id
    instance_type = "t3.small"
    vpc_security_group_ids = [aws_security_group.app_sg.id]
    key_name = aws_key_pair.deployer.key_name
    root_block_device {
      volume_size = 20
      volume_type = "gp3"

    }
    user_data = <<-EOF
        #!/bin/bash
        set -x # print each command before executing
        exec >> /var/log/user-data.log 2>&1 # route errors to that file
        dnf install -y git

        sudo dnf install -y docker
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker ec2-user

        sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m) -o /usr/libexec/docker/cli-plugins/docker-compose
        sudo chmod +x /usr/libexec/docker/cli-plugins/docker-compose
        docker compose version

        mkdir -p ~/.docker/cli-plugins
        BUILDX_VERSION=$(curl -s https://api.github.com/repos/docker/buildx/releases/latest | grep -oP '"tag_name": "\K[^"]+')
        curl -L https://github.com/docker/buildx/releases/download/$${BUILDX_VERSION}/buildx-$${BUILDX_VERSION}.linux-amd64 -o ~/.docker/cli-plugins/docker-buildx
        chmod +x ~/.docker/cli-plugins/docker-buildx
        docker buildx version

        # Clone and start app
        git clone https://github.com/arifekrem/RecEngine-Mthree.git /rec_engine
        cd /rec_engine
        docker compose up -d --build   # -d = detached (runs in background)
    EOF
  
  tags = {
    Name = "learning_terraform"
  } # sets the instance name
}

output "instance_public_ip" {
  value       = aws_instance.app.public_ip
  description = "SSH: ssh ec2-user@$(terraform output -raw instance_public_ip)"
}