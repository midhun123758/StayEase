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

data "aws_vpc" "default" {
default = true
}

data "aws_subnets" "default" {
filter {
name   = "vpc-id"
values = [data.aws_vpc.default.id]
}
}

variable "existing_ec2_sg_id" {
description = "Current StayEase EC2 security group ID"
type        = string
default     = "sg-076931eb177ba0992"
}

variable "rds_password" {
description = "Password for StayEase RDS PostgreSQL"
type        = string
sensitive   = true
}

resource "aws_security_group" "stayease_rds_sg" {
name        = "stayease-rds-security-group"
description = "Allow PostgreSQL access from current StayEase EC2"
vpc_id      = data.aws_vpc.default.id

ingress {
from_port       = 5432
to_port         = 5432
protocol        = "tcp"
security_groups = [var.existing_ec2_sg_id]
}

egress {
from_port   = 0
to_port     = 0
protocol    = "-1"
cidr_blocks = ["0.0.0.0/0"]
}

tags = {
Name = "stayease-rds-sg"
}
}

resource "aws_db_subnet_group" "stayease_rds_subnet_group" {
name       = "stayease-rds-subnet-group"
subnet_ids = data.aws_subnets.default.ids

tags = {
Name = "stayease-rds-subnet-group"
}
}

resource "aws_db_instance" "stayease_rds" {
identifier             = "stayease-db"
engine                 = "postgres"
instance_class         = "db.t3.micro"
allocated_storage      = 20
storage_type           = "gp3"
storage_encrypted      = true

db_name                = "stayease"
username               = "stayease_user"
password               = var.rds_password
port                   = 5432
publicly_accessible    = false
db_subnet_group_name   = aws_db_subnet_group.stayease_rds_subnet_group.name
vpc_security_group_ids = [aws_security_group.stayease_rds_sg.id]

backup_retention_period = 7
skip_final_snapshot     = true
deletion_protection     = false

tags = {
Name = "stayease-rds"
}
}

output "rds_endpoint" {
value = aws_db_instance.stayease_rds.address
}
