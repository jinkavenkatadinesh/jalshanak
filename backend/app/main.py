import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.auth import get_password_hash
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import LeakReport, StatusHistory, User, Verification
from app.routers import admin, auth, reports

# Initialize Database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend services for JalRakshak Smart Water Leak Reporting System - Hyderabad/Telangana division.",
    version="1.0.0",
)

# Set up CORS middleware to connect seamlessly with React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development. Can narrow down in production settings.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists and mount it to serve images statically
upload_path = Path(settings.UPLOAD_DIR)
upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(auth.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


# Serve React Frontend Static Files (useful for single-container deploys like Hugging Face Spaces)
frontend_dist_path = Path("frontend/dist")
if not frontend_dist_path.exists():
    frontend_dist_path = Path("../frontend/dist")

if frontend_dist_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist_path), html=True), name="frontend")
else:

    @app.get("/")
    def read_root():
        return {
            "status": "online",
            "service": "JalRakshak API Hub",
            "region": "Telangana (Hyderabad)",
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }


# Database Seeding Function
@app.on_event("startup")
def seed_data():
    db = SessionLocal()
    try:
        # 1. Seed Default Admin User
        admin_email = "admin@jalrakshak.org"
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            admin_user = User(
                name="HMWS&SB Administrator",  # Hyderabad Metropolitan Water Supply and Sewerage Board
                email=admin_email,
                password_hash=get_password_hash("admin123"),
                role="admin",
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=10),
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("Seeded default administrator: admin@jalrakshak.org / admin123")

        # 2. Seed Default Citizen Users
        citizen_1_email = "shanker@gmail.com"
        citizen_1 = db.query(User).filter(User.email == citizen_1_email).first()
        if not citizen_1:
            citizen_1 = User(
                name="Jaishankar Prasad",
                email=citizen_1_email,
                password_hash=get_password_hash("citizen123"),
                role="citizen",
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=8),
            )
            db.add(citizen_1)

        citizen_2_email = "anitha.reddy@gmail.com"
        citizen_2 = db.query(User).filter(User.email == citizen_2_email).first()
        if not citizen_2:
            citizen_2 = User(
                name="Anitha Reddy",
                email=citizen_2_email,
                password_hash=get_password_hash("citizen123"),
                role="citizen",
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=7),
            )
            db.add(citizen_2)

        db.commit()

        # Retrieve freshly created or existing citizen IDs for report binding
        c1 = db.query(User).filter(User.email == citizen_1_email).first()
        c2 = db.query(User).filter(User.email == citizen_2_email).first()
        admin_u = db.query(User).filter(User.email == admin_email).first()

        # 3. Seed Leak Reports
        if db.query(LeakReport).count() == 0:
            reports_to_seed = [
                LeakReport(
                    user_id=c1.id,
                    title="Gushing Main Water Pipeline Burst",
                    description="A major water pipeline has burst near Gachibowli Flyover, causing massive flooding on the main road. Hundreds of gallons of clean drinking water are leaking every minute.",
                    latitude=17.4435,
                    longitude=78.3812,
                    status="In Progress",
                    verification_count=3,
                    severity="High",
                    created_at=datetime.datetime.utcnow() - datetime.timedelta(days=2),
                ),
                LeakReport(
                    user_id=c2.id,
                    title="Roadside Joint Seepage",
                    description="Minor joint seepage on the pathway near Jubilee Hills Checkpost. Slow water pooling is starting to form. Needs early repair to prevent road erosion.",
                    latitude=17.4216,
                    longitude=78.4189,
                    status="Under Review",
                    verification_count=1,
                    severity="Medium",
                    created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=18),
                ),
                LeakReport(
                    user_id=c1.id,
                    title="Drinking Water Valve Dripping",
                    description="A distribution valve is slowly dripping continuously near Lad Bazar, Charminar. Citizens are placing buckets under it. Please fix the rubber gaskets.",
                    latitude=17.3616,
                    longitude=78.4747,
                    status="Resolved",
                    verification_count=4,
                    severity="Low",
                    created_at=datetime.datetime.utcnow() - datetime.timedelta(days=4),
                ),
                LeakReport(
                    user_id=c2.id,
                    title="Secunderabad Station Leakage",
                    description="Heavy water spraying from a municipal overhead tank outlet near Secunderabad Station platform 1 entrance. Flooding the local sidewalk.",
                    latitude=17.4338,
                    longitude=78.5015,
                    status="Reported",
                    verification_count=0,
                    severity="High",
                    created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2),
                ),
            ]
            db.add_all(reports_to_seed)
            db.commit()

            # Retrieve seeded reports
            r1 = db.query(LeakReport).filter(LeakReport.title.like("%Gushing%")).first()
            db.query(LeakReport).filter(LeakReport.title.like("%Roadside%")).first()
            r3 = db.query(LeakReport).filter(LeakReport.title.like("%Drinking%")).first()

            # 4. Seed Status History (Remarks timeline)
            histories = [
                # Report 1 history
                StatusHistory(
                    report_id=r1.id,
                    old_status="Reported",
                    new_status="Under Review",
                    remarks="HMWS&SB engineers assigned. Inspecting the source point.",
                    changed_by=admin_u.id,
                    changed_at=datetime.datetime.utcnow() - datetime.timedelta(days=1, hours=12),
                ),
                StatusHistory(
                    report_id=r1.id,
                    old_status="Under Review",
                    new_status="In Progress",
                    remarks="Welding equipment and replacement pipe dispatched. Excavation begun.",
                    changed_by=admin_u.id,
                    changed_at=datetime.datetime.utcnow() - datetime.timedelta(days=1),
                ),
                # Report 3 history
                StatusHistory(
                    report_id=r3.id,
                    old_status="Reported",
                    new_status="Under Review",
                    remarks="Assigned to Area 4 local maintenance unit.",
                    changed_by=admin_u.id,
                    changed_at=datetime.datetime.utcnow() - datetime.timedelta(days=3),
                ),
                StatusHistory(
                    report_id=r3.id,
                    old_status="Under Review",
                    new_status="Resolved",
                    remarks="Gaskets replaced. Seepage successfully arrested and double-checked.",
                    changed_by=admin_u.id,
                    changed_at=datetime.datetime.utcnow() - datetime.timedelta(days=2),
                ),
            ]
            db.add_all(histories)

            # 5. Seed Peer Verifications
            verifications = [
                Verification(
                    report_id=r1.id,
                    user_id=c2.id,
                    verified_at=datetime.datetime.utcnow() - datetime.timedelta(days=1, hours=20),
                ),
                Verification(
                    report_id=r3.id,
                    user_id=c1.id,
                    verified_at=datetime.datetime.utcnow() - datetime.timedelta(days=3, hours=10),
                ),
            ]
            db.add_all(verifications)
            db.commit()

            print("Seeded database with sample Hyderabad leak reports, verifications, and histories.")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()
