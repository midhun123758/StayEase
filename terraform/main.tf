terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "eu-north-1"
}

resource "aws_security_group" "stayease_sg" {
  name        = "stayease-security-group"
  description = "StayEase security group"

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

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "stayease-sg"
  }
}

resource "aws_instance" "stayease_server" {
  ami                    = "ami-09a9858973b288bdd"  # Ubuntu 22.04 eu-north-1
  instance_type          = "t3.micro"
  key_name               = "stayease-key"
  vpc_security_group_ids = [aws_security_group.stayease_sg.id]

  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io docker-compose-plugin awscli git
    usermod -aG docker ubuntu
    systemctl enable docker
    systemctl start docker
    cd /home/ubuntu
    git clone https://github.com/midhun123758/StayEase.git
    chown -R ubuntu:ubuntu stayease
  EOF

  tags = {
    Name = "StayEaseServer"
  }
}

resource "aws_eip" "stayease_eip" {
  instance = aws_instance.stayease_server.id
  domain   = "vpc"

  tags = {
    Name = "stayease-eip"
  }
}
