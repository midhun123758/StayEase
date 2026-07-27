# 🏨 StayEase

**StayEase** is a modern, microservices-oriented accommodation and hostel management platform. It connects hostel owners with students and professionals looking for accommodations while leveraging AI to provide smart search, concierge services, and automated billing.

---

## 📖 Why this README exists?

In the software engineering world, a `README.md` is considered the most important document in a project. It serves as:
1. **The "Front Page" of the Project:** When employers, recruiters, or other developers look at your GitHub profile, the `README.md` is the very first thing they see. It acts like a landing page that shows off what your project is and how complex it is.
2. **Onboarding Manual:** If another developer is hired to help build StayEase, this README tells them exactly how to install Docker, what environment variables they need, and how to run the project locally.
3. **Personal Reference Guide:** Months from now, this document will serve as a personal manual to remember exactly how the microservices architecture, RabbitMQ connections, and AI Service operate.

Think of this README as the **Instruction Manual** for your codebase!

---

## 🚀 Key Features

* **Multi-Role Access Control:** Custom dashboards and capabilities for `Admins`, `Owners` (Hostel Management), `Hostlers` (Staff), and `Clients` (Tenants).
* **AI-Powered Concierge:** Integrated FastAPI service with **Google Gemini Flash Lite** and **Qdrant Vector Database** for semantic search and conversational AI hostel recommendations.
* **Automated Billing & Meals:** Scheduled background tasks via **Celery & Redis** to automatically generate monthly bills and track minute-by-minute meal charges.
* **KYC & Payments:** Integrated user KYC verification, automated Razorpay payment handling, and UPI integrations.
* **Real-time Capabilities:** Django Channels with Redis for WebSockets.
* **Infrastructure as Code:** Fully codified AWS infrastructure (EC2, ECR, Elastic IPs, Security Groups) using **Terraform**.
* **Automated CI/CD:** Zero-downtime deployment pipelines using **GitHub Actions**, Docker Compose, and AWS ECR.

---

## 🏗️ Architecture & Tech Stack

### Core Technologies
- **Backend Framework:** Django (Python 3.12)
- **AI Microservice:** FastAPI (Python)
- **Database:** PostgreSQL 15
- **Message Broker:** RabbitMQ
- **Caching & Celery Broker:** Redis 7
- **Vector Database (AI):** Qdrant
- **Web Server / Reverse Proxy:** Nginx & Daphne (ASGI)

### Cloud & DevOps
- **Cloud Provider:** Amazon Web Services (AWS)
- **Containerization:** Docker & Docker Compose
- **Infrastructure Provisioning:** Terraform
- **CI/CD:** GitHub Actions

### System Flow
1. **Client Requests** hit the **Nginx** reverse proxy on EC2.
2. Nginx routes traffic to either the **Django API** (Port 8000) or the **AI FastAPI Service** (Port 8001).
3. The **Django API** handles business logic, interacting with PostgreSQL, and queues background tasks (billing, notifications) into **RabbitMQ/Redis**.
4. **Celery Workers** process these background tasks asynchronously.
5. The **AI Service** handles natural language queries by embedding them and querying the **Qdrant Vector DB**, then synthesizing responses using the **Google Gemini API**.

---

## 📂 Project Structure

```text
Backend.StayEase/
│
├── StayEase/                  # Core Django Backend
│   ├── App/                   # Core Models (Users, Roles, KYC)
│   ├── Admin_panel/           # Superadmin endpoints
│   ├── Base_Panel/            # Shared components and utilities
│   ├── Client_panel/          # Tenant-facing endpoints (Search, Booking)
│   ├── Hostlers_panel/        # Owner-facing endpoints (Rooms, Billing, Management)
│   └── StayEase/              # Core Settings, ASGI/WSGI, Celery config
│
├── Ai_service/                # FastAPI Microservice for AI Concierge
│   ├── app/
│   │   ├── main.py            # FastAPI Routes (e.g., /ask)
│   │   ├── ai_service.py      # Qdrant search and Gemini integrations
│   │   └── worker.py          # RabbitMQ consumer for AI sync
│
├── terraform/                 # Infrastructure as Code
│   └── main.tf                # AWS EC2, EBS, ECR, Security Group definitions
│
├── .github/workflows/         # CI/CD Pipelines
│   └── ci-cd.yml              # Automated testing, building, and EC2 deployment
│
├── nginx/                     # Nginx Configuration
│   └── default.conf           # Reverse proxy routing rules
│
├── docker-compose.yml         # Local Development Compose file
└── docker-compose.prod.yml    # Production Compose file
```

---

## 🛠️ Local Development Setup

To run the entire StayEase microservice ecosystem locally, follow these steps:

### 1. Prerequisites
Ensure you have the following installed:
- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/)

### 2. Environment Variables
You need to set up environment variables for both Django and the AI service. 

Create a `.env` file inside the `StayEase/` directory:
```env
# StayEase/.env
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=stayease_db
DB_USER=stayease_user
DB_PASSWORD=your_secure_password
DB_HOST=stayease_db
DB_PORT=5432

AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_STORAGE_BUCKET_NAME=your_bucket
AWS_S3_REGION_NAME=eu-north-1

CLOUDINARY_CLOUD_NAME=your_cloudinary_name
CLOUDINARY_API_KEY=your_cloudinary_key
CLOUDINARY_API_SECRET=your_cloudinary_secret

RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret

EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

Create a `.env` file inside the `Ai_service/` directory:
```env
# Ai_service/.env
GEMINI_API_KEY=your_google_gemini_api_key
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
QDRANT_HOST=qdrant
QDRANT_PORT=6333
```

### 3. Build and Run via Docker Compose
From the root directory of the project, run:
```bash
docker-compose up --build
```
*This will spin up PostgreSQL, Redis, RabbitMQ, Qdrant, the Django web server, Celery workers, the Celery beat scheduler, the AI FastAPI service, the AI RabbitMQ worker, and Nginx.*

### 4. Run Migrations
Once the containers are running, apply the database migrations:
```bash
docker-compose exec stayease_web python manage.py migrate
```

### 5. Access the Application
- **Django API:** `http://localhost:8000`
- **Swagger Documentation:** `http://localhost:8000/api/schema/swagger-ui/`
- **AI Service API:** `http://localhost:8002`

---

## ☁️ Deployment & Infrastructure

The project infrastructure is hosted on **AWS (eu-north-1)** and managed via **Terraform**. 

### Infrastructure Highlights
- **AWS EC2 (t3.small):** Runs the production Docker Compose stack.
- **EBS Volume (20 GB):** Automatically expanded to accommodate multiple ML and application containers.
- **AWS ECR:** Stores versioned Docker images for the Django app and AI service.
- **Local Postgres Fallback:** Due to IAM restrictions on RDS, the production database runs securely inside a Docker volume on the EC2 instance, continuously backed up.

### CI/CD Pipeline
Deployment is fully automated using GitHub Actions (`.github/workflows/ci-cd.yml`).
1. **Test Job:** Spins up ephemeral containers, waits for PostgreSQL to become healthy, and runs `manage.py test`.
2. **Build Job:** Builds Docker images and pushes them to AWS ECR.
3. **Deploy Job:** SSH's into the EC2 instance, cleans up old Docker logs and dangling images (preventing disk exhaustion), pulls the latest ECR images, runs migrations, and restarts the containers seamlessly.

---

## 🤖 AI Service Architecture

The AI service operates as a standalone microservice to prevent heavy Machine Learning operations from blocking the main Django application. 
- When hostel data is added or updated in Django, a message is published to **RabbitMQ**.
- The `ai_worker` consumes this message and updates embeddings in the **Qdrant Vector Database**.
- The `/ask` endpoint in FastAPI takes user queries, performs a semantic similarity search in Qdrant, builds context, and uses **Google Gemini** to generate natural, conversational responses.

---
*Maintained by the StayEase Development Team.*
