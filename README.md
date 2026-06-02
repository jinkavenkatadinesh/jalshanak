---
title: JalRakshak
emoji: 💧
colorFrom: blue
colorTo: cyan
sdk: docker
app_port: 7860
license: agpl-3.0
---

# 💧 JalRakshak – Smart Water Leak Reporting System

**JalRakshak** is a state-of-the-art CivicTech full-stack web application designed for the Hyderabad and Telangana Metropolitan division. It empowers citizens to easily report public water leakages using photos and browser Geolocation APIs, while providing city authorities (like HMWS&SB) with an advanced analytics portal to review, prioritize, verify, and resolve leakage tickets.

---

## 🚀 Key Features

### 👤 Citizen Capabilities
* **Auto GPS Snapping**: Snaps browser location coordinates automatically on report opening, centering custom pins in Hyderabad.
* **Photo Proof Upload**: Supports drag-and-drop or click file loaders for water leakage image evidence.
* **Smart Proximity Duplicate Alert**: Instantly checks and warns citizens if another unresolved report exists within 100 meters.
* **Peer-to-Peer Verification**: Citizens can vote on other citizens' reports, boosting report credibility metrics.
* **Interactive Leaflet Map**: Render status-colored custom markers on a dark-themed map canvas.

### 🏢 Authority / Admin Capabilities
* **Interactive KPI Aggregates**: High-level visual statistics counting total active, pending, and resolved leakages.
* **Responsive Distribution Charts**: Area-wise bars, status splits, and severity divisions.
* **Split-View Details Inspector**: Multi-column sorting datagrid linked to an inspection details side-drawer.
* **Diagnostics remarks & Timelines**: Transitions issue states (Reported ➔ Under Review ➔ In Progress ➔ Resolved) with logging timeline remarks.

---

## 🛠️ Technology Stack

* **Frontend**: React.js (Vite), React Router, Axios, Lucide Icons, Leaflet Maps with OpenStreetMap.
* **Backend**: FastAPI, SQLAlchemy ORM, Pydantic v2 validation.
* **Database**: PostgreSQL (Production) / SQLite (Zero-config local sandbox fallback).
* **Containerization**: Docker, Docker Compose, Nginx.
* **Styling**: Premium Custom Vanilla CSS (Dark-ocean themed, Glassmorphism, animations).

---

## 📂 Project Structure

```
d:\jaishanak\
├── backend\
│   ├── app\
│   │   ├── routers\         # Routers (auth, reports, admin)
│   │   ├── ai_engine.py     # Heuristics severity & duplicate checkers
│   │   ├── auth.py          # JWT, passwords encryption
│   │   ├── config.py        # Settings configuration loads
│   │   ├── database.py      # SQLAlchemy DB engine
│   │   ├── models.py        # Database models declarations
│   │   └── schemas.py       # Pydantic validation structures
│   ├── uploads\             # Local media storage directory
│   ├── Dockerfile
│   └── requirements.txt
├── frontend\
│   ├── src\
│   │   ├── assets\
│   │   ├── components\      # MapView, ReportModal, Timeline, Navbar
│   │   ├── context\         # Auth React state distributions
│   │   ├── pages\           # Login, Register, Dashboards
│   │   ├── services\        # Axios interceptors API layer
│   │   ├── App.jsx          # Route configurations
│   │   └── index.css        # Vanilla CSS variable design system
│   ├── Dockerfile
│   ├── nginx.conf
│   └── index.html
├── docker-compose.yml
├── .env                     # Local settings templates
└── README.md
```

---

## 🚦 Installation & Run Guide

### Option 1: Quick Local Development (Zero-Config SQLite fallback)

Ensure you have **Python 3.10+** and **Node.js 18+** installed.

#### 1. Launch Backend API Server
```bash
cd backend
# Create virtual environment
python -m venv venv
# Activate virtual environment (Windows)
.\venv\Scripts\activate
# Install requirements
pip install -r requirements.txt
# Run FastAPI with Uvicorn
uvicorn app.main:app --reload
```
The API server starts at `http://localhost:8000`. Swagger API docs are accessible at `http://localhost:8000/docs`.

#### 2. Launch React Frontend
Open a new terminal shell:
```bash
cd frontend
# Install package dependencies
npm install
# Start React Vite Server
npm run dev
```
The frontend web application runs at `http://localhost:5173`.

---

### Option 2: Full Docker Containerization (PostgreSQL Service)

Build and boot all containers (FastAPI, Nginx, and Postgres) in a single run:
```bash
# Run at the project root directory
docker-compose up --build
```
* **React Web Frontend**: `http://localhost:3000`
* **FastAPI Backend Services**: `http://localhost:8000`
* **PostgreSQL Server**: `localhost:5432`

---

### Option 3: Enterprise Production Deployment (SSL Gateway & Multi-stage Containers)

For production environments, JalRakshak containerizes the frontend compiled asset server, backend API hub, and PostgreSQL persistence with a unified secure SSL reverse-proxy gateway (Nginx).

#### 1. Setup Production Environment variables
Create a `.env.prod` (or rename `.env` in production) containing your live configurations:
```env
# --- Production Settings ---
DB_PASSWORD=your_ultra_secure_db_password
SECRET_KEY=your_production_jwt_signing_key
VITE_API_BASE_URL=/api
VITE_BACKEND_URL=
```

#### 2. Boot the Production Stack
Run the production orchestrator:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```
This builds and launches four self-healing containers:
* **`jalrakshak_postgres_prod`**: Core PostgreSQL engine.
* **`jalrakshak_backend_prod`**: High-performance FastAPI REST API.
* **`jalrakshak_frontend_prod`**: Lightweight Nginx serving Vite compiled production bundle.
* **`jalrakshak_nginx_prod`**: Unified web gateway reverse proxying SSL (HTTPS), forwarding REST requests, and caching static assets.

#### 3. Let's Encrypt SSL Bootstrapping (Chicken-and-Egg Workaround)
Since `nginx.prod.conf` requires the certificate files to boot, but Certbot needs Nginx running to verify the domain via port 80, follow this standard bootstrapping procedure on your live server:

1. **Temporary Non-SSL Boot**:
   In `nginx.prod.conf`, temporarily comment out the server block listening on `443 ssl` (lines 21-61), and comment out the HTTPS redirect in the port 80 block (lines 15-18).
2. **Launch Nginx**:
   Run `docker-compose -f docker-compose.prod.yml up -d web_gateway` to start Nginx on HTTP port 80.
3. **Generate Live Certificates**:
   Run a temporary Certbot container to fetch real certificates:
   ```bash
   docker run --rm \
     -v jalshanak_certbot_certs:/etc/letsencrypt \
     -v jalshanak_certbot_www:/var/www/certbot \
     certbot/certbot certonly --webroot \
     -w /var/www/certbot \
     -d yourdomain.com -d www.yourdomain.com \
     --email admin@yourdomain.com --agree-tos --no-eff-email
   ```
4. **Restore configuration and Reload**:
   Uncomment the lines in `nginx.prod.conf` and reload Nginx:
   ```bash
   docker-compose -f docker-compose.prod.yml exec web_gateway nginx -s reload
   ```

---

## 🔑 Sandboxed Demo Logins

At start-up, the database is auto-seeded with mock citizens, status timelines, and reported leakages in Hyderabad neighborhoods. You can sign in with:

| User Profile | Email Credentials | Password |
|---|---|---|
| **Citizen User** | `shanker@gmail.com` | `citizen123` |
| **HMWS&SB Authority Admin** | `admin@jalrakshak.org` | `admin123` |

You can also use the interactive **Quick Demo Account Credentials** button triggers directly in the login UI to sign in in 1-click!

---

## 🧪 Operational Workflow

1. **Submit**: Sign in as a **Citizen**, tap **Report Leak**, upload an image, and submit the mock GPS coordinates.
2. **AI Scan**: The AI engine runs on upload, analyzing keywords to rank severity and checking for duplicates.
3. **Verify**: Log in as *another* citizen and tap **Confirm Active Leak** on the card or map popup to boost its verification count.
4. **Resolve**: Log in as **Authority Admin**, select the issue, view AI coordinates diagnostics, choose status `"In Progress"` or `"Resolved"`, add Remarks, and apply the status update to record the timeline entry.
