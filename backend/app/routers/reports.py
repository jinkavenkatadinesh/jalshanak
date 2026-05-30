import uuid
import shutil
import datetime
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app import models, schemas, auth
from app.database import get_db
from app.ai_engine import analyze_leak_image, check_for_duplicate_reports

router = APIRouter(prefix="/reports", tags=["Leak Reports"])

@router.get("", response_model=List[schemas.LeakReportOut])
def list_reports(
    status_filter: Optional[str] = None,
    user_id_filter: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Fetch all water leak reports. Includes filters for status and individual user reports.
    """
    query = db.query(
        models.LeakReport.id,
        models.LeakReport.user_id,
        models.LeakReport.title,
        models.LeakReport.description,
        models.LeakReport.image_url,
        models.LeakReport.latitude,
        models.LeakReport.longitude,
        models.LeakReport.status,
        models.LeakReport.verification_count,
        models.LeakReport.severity,
        models.LeakReport.created_at,
        models.LeakReport.updated_at,
        models.User.name.label("reporter_name")
    ).join(models.User, models.LeakReport.user_id == models.User.id)
    
    if status_filter:
        query = query.filter(models.LeakReport.status == status_filter)
    if user_id_filter:
        query = query.filter(models.LeakReport.user_id == user_id_filter)
        
    query = query.order_by(desc(models.LeakReport.created_at))
    results = query.all()
    
    # Map raw queries to schema objects
    reports = []
    for r in results:
        reports.append(
            schemas.LeakReportOut(
                id=r.id,
                user_id=r.user_id,
                title=r.title,
                description=r.description,
                image_url=r.image_url,
                latitude=r.latitude,
                longitude=r.longitude,
                status=r.status,
                verification_count=r.verification_count,
                severity=r.severity,
                created_at=r.created_at,
                updated_at=r.updated_at,
                reporter_name=r.reporter_name
            )
        )
    return reports

@router.post("", response_model=schemas.LeakReportOut, status_code=status.HTTP_201_CREATED)
def create_report(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    latitude: float = Form(...),
    longitude: float = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Submit a new water leakage report with optional images and browser GPS coordinates.
    Triggers simulated AI image verification and flags proximity duplicates.
    """
    # 1. Handle file upload if present
    image_url = None
    filename_str = ""
    if image and image.filename:
        upload_dir = Path("uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_ext = Path(image.filename).suffix
        unique_name = f"{uuid.uuid4()}{file_ext}"
        file_path = upload_dir / unique_name
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            
        image_url = f"/uploads/{unique_name}"
        filename_str = image.filename

    # 2. Trigger AI Engine Simulation
    ai_results = analyze_leak_image(description or "", filename_str)
    detected_severity = ai_results["severity"]
    
    # 3. Duplicate check (within 100 meters)
    duplicates = check_for_duplicate_reports(db, latitude, longitude, max_distance_meters=100.0)
    if duplicates:
        # We can append warning messages to the description in the DB, or just note it.
        # We will prefix duplicate warning metadata in description for visibility
        description = f"[SYSTEM: High probability duplicate of report #{duplicates[0]['id']} within {duplicates[0]['distance_meters']}m] " + (description or "")

    # 4. Save to Database
    new_report = models.LeakReport(
        user_id=current_user.id,
        title=title,
        description=description,
        image_url=image_url,
        latitude=latitude,
        longitude=longitude,
        status="Reported",
        verification_count=0,
        severity=detected_severity
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    # Inject reporter name for direct frontend rendering compatibility
    new_report_schema = schemas.LeakReportOut.model_validate(new_report)
    new_report_schema.reporter_name = current_user.name
    
    return new_report_schema

@router.get("/{id}", response_model=schemas.LeakReportOut)
def get_report_details(id: int, db: Session = Depends(get_db)):
    """
    Retrieve comprehensive information for a single leak report.
    """
    report = db.query(models.LeakReport).filter(models.LeakReport.id == id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Leak report not found")
        
    reporter = db.query(models.User).filter(models.User.id == report.user_id).first()
    
    report_schema = schemas.LeakReportOut.model_validate(report)
    report_schema.reporter_name = reporter.name if reporter else "Unknown Reporter"
    return report_schema

@router.post("/{id}/verify", response_model=schemas.LeakReportOut)
def verify_report(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Allows citizens to verify a reported leak. 
    Prevents self-verifications and repeated verifications.
    """
    report = db.query(models.LeakReport).filter(models.LeakReport.id == id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Leak report not found")
        
    # Prevent self-verification
    if report.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot verify your own reported water leak issue."
        )
        
    # Check if already verified
    existing_verification = db.query(models.Verification).filter(
        models.Verification.report_id == id,
        models.Verification.user_id == current_user.id
    ).first()
    
    if existing_verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already verified this report."
        )
        
    # Create verification entry
    verification = models.Verification(
        report_id=id,
        user_id=current_user.id
    )
    db.add(verification)
    
    # Increment count
    report.verification_count += 1
    db.commit()
    db.refresh(report)
    
    reporter = db.query(models.User).filter(models.User.id == report.user_id).first()
    
    report_schema = schemas.LeakReportOut.model_validate(report)
    report_schema.reporter_name = reporter.name if reporter else "Unknown Reporter"
    return report_schema
