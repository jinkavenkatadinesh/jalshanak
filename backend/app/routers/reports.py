import datetime
import shutil
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.ai_engine import analyze_leak_image, check_for_duplicate_reports
from app.database import get_db

router = APIRouter(prefix="", tags=["Leak Reports & Notifications"])

# --- Notifications Endpoints ---


@router.get("/notifications", response_model=List[schemas.NotificationOut])
def get_user_notifications(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    Retrieves all notifications logged for the current active user.
    """
    notifications = (
        db.query(models.Notification)
        .filter(models.Notification.user_id == current_user.id)
        .order_by(desc(models.Notification.created_at))
        .all()
    )
    return notifications


@router.put("/notifications/{id}/read", response_model=schemas.NotificationOut)
def mark_notification_read(
    id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)
):
    """
    Marks a specific notification entry as read (is_read=1).
    """
    notif = (
        db.query(models.Notification)
        .filter(models.Notification.id == id, models.Notification.user_id == current_user.id)
        .first()
    )

    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = 1
    db.commit()
    db.refresh(notif)
    return notif


# --- Leak Reports Endpoints ---


@router.get("/reports", response_model=List[schemas.LeakReportOut])
def list_reports(
    status_filter: Optional[str] = None, user_id_filter: Optional[int] = None, db: Session = Depends(get_db)
):
    """
    Fetch all water leak reports. Sorted by priority_score descending (bubbling critical issues to the top),
    then by creation date.
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
        models.LeakReport.image_url_after,
        models.LeakReport.priority_score,
        models.LeakReport.daily_loss,
        models.LeakReport.created_at,
        models.LeakReport.updated_at,
        models.User.name.label("reporter_name"),
    ).join(models.User, models.LeakReport.user_id == models.User.id)

    if status_filter:
        query = query.filter(models.LeakReport.status == status_filter)
    if user_id_filter:
        query = query.filter(models.LeakReport.user_id == user_id_filter)

    # Priority sorting bubbles up critical top-score leaks first
    query = query.order_by(desc(models.LeakReport.priority_score), desc(models.LeakReport.created_at))
    results = query.all()

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
                image_url_after=r.image_url_after,
                priority_score=r.priority_score,
                daily_loss=r.daily_loss,
                created_at=r.created_at,
                updated_at=r.updated_at,
                reporter_name=r.reporter_name,
            )
        )
    return reports


@router.post("/reports", response_model=schemas.LeakReportOut, status_code=status.HTTP_201_CREATED)
def create_report(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    latitude: float = Form(...),
    longitude: float = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    Submit a water leakage report.
    Triggers visual AI image analysis, parses EXIF geolocations, and checks duplicates within 100 meters using Haversine formula.
    If a duplicate open leak exists, it automatically merges the report as a verification vote.
    """
    # 1. Handle file upload if present
    image_url = None
    filename_str = ""
    saved_filepath = None
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
        saved_filepath = str(file_path)

    # 2. Run AI Engine (extracts EXIF GPS and analyzes visual colors)
    ai_results = analyze_leak_image(description or "", filename_str, saved_filepath)
    detected_severity = ai_results["severity"]
    daily_loss = ai_results["daily_loss"]
    priority_score = ai_results["priority_score"]
    ai_remarks = ai_results["ai_remarks"]

    # 3. Geo-metadata snap: Overwrite coordinates if embedded EXIF GPS tags exist
    if ai_results.get("exif_gps"):
        latitude = ai_results["exif_gps"]["latitude"]
        longitude = ai_results["exif_gps"]["longitude"]

    # 4. Proximity Duplicate Merging (100m radius check via Haversine)
    duplicates = check_for_duplicate_reports(db, latitude, longitude, max_distance_meters=100.0)
    if duplicates:
        # Find the primary active duplicate report
        dup_report = db.query(models.LeakReport).filter(models.LeakReport.id == duplicates[0]["id"]).first()

        # Verify it if this user is not the original reporter and hasn't voted already
        if dup_report.user_id != current_user.id:
            existing_verify = (
                db.query(models.Verification)
                .filter(models.Verification.report_id == dup_report.id, models.Verification.user_id == current_user.id)
                .first()
            )

            if not existing_verify:
                # Add verification vote
                verify_vote = models.Verification(report_id=dup_report.id, user_id=current_user.id)
                db.add(verify_vote)
                dup_report.verification_count += 1

                # Re-calculate Priority Score
                sev_factors = {"High": 3, "Medium": 2, "Low": 1}
                factor = sev_factors.get(dup_report.severity, 2)
                dup_report.priority_score = factor * (dup_report.verification_count + 1)

        # Log merge notifications alert for the citizen
        merge_msg = f"[DUPLICATE MERGE] An active water leak already exists at this location! Your report was merged as a verification vote on '{dup_report.title}' to boost its repair priority."
        notif = models.Notification(user_id=current_user.id, report_id=dup_report.id, message=merge_msg)
        db.add(notif)
        db.commit()
        db.refresh(dup_report)

        # Retrieve reporter profile
        reporter = db.query(models.User).filter(models.User.id == dup_report.user_id).first()
        dup_schema = schemas.LeakReportOut.model_validate(dup_report)
        dup_schema.reporter_name = reporter.name if reporter else "Unknown Reporter"

        # Bounce with the merged ticket info to prevent database bloating
        return dup_schema

    # 5. No duplicates found: create new report
    # Auto-assign engineer team based on neighborhood coordinates
    assigned_engineer = "HMWS&SB District Dispatch Team"
    if abs(latitude - 17.44) < 0.05 and abs(longitude - 78.38) < 0.05:
        assigned_engineer = "HMWS&SB Team Alpha (Gachibowli)"
    elif abs(latitude - 17.40) < 0.05 and abs(longitude - 78.44) < 0.05:
        assigned_engineer = "HMWS&SB Team Beta (Jubilee Hills)"
    elif abs(latitude - 17.48) < 0.05 and abs(longitude - 78.55) < 0.05:
        assigned_engineer = "Secunderabad Maintenance Crew"
    elif abs(latitude - 17.36) < 0.05 and abs(longitude - 78.47) < 0.05:
        assigned_engineer = "Old City Rapid Repair Division"

    assigned_date = datetime.datetime.utcnow()

    # SLA expected completion hour calculator
    sla_hours = 48  # Medium severity default
    if detected_severity == "High":
        sla_hours = 24
    elif detected_severity == "Low":
        sla_hours = 72

    expected_completion = assigned_date + datetime.timedelta(hours=sla_hours)

    # Append real AI Diagnostics directly to the description
    final_description = description or ""
    if ai_remarks:
        final_description += f"\n\n[AI Diagnostics]\n{ai_remarks}"

    new_report = models.LeakReport(
        user_id=current_user.id,
        title=title,
        description=final_description,
        image_url=image_url,
        latitude=latitude,
        longitude=longitude,
        status="Reported",
        verification_count=0,
        severity=detected_severity,
        priority_score=priority_score,
        daily_loss=daily_loss,
        assigned_engineer=assigned_engineer,
        assigned_date=assigned_date,
        expected_completion=expected_completion,
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    new_report_schema = schemas.LeakReportOut.model_validate(new_report)
    new_report_schema.reporter_name = current_user.name

    return new_report_schema


@router.get("/reports/{id}", response_model=schemas.LeakReportOut)
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


@router.post("/reports/{id}/verify", response_model=schemas.LeakReportOut)
def verify_report(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    Allows citizens to verify a reported leak.
    Prevents self-verifications and repeated verifications.
    Calculates priority scores and sends alert notifications to the reporter.
    """
    report = db.query(models.LeakReport).filter(models.LeakReport.id == id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Leak report not found")

    # Prevent self-verification
    if report.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot verify your own reported water leak issue."
        )

    # Check if already verified
    existing_verification = (
        db.query(models.Verification)
        .filter(models.Verification.report_id == id, models.Verification.user_id == current_user.id)
        .first()
    )

    if existing_verification:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already verified this report.")

    # Create verification entry
    verification = models.Verification(report_id=id, user_id=current_user.id)
    db.add(verification)

    # Increment count and recompute priority
    report.verification_count += 1

    sev_factors = {"High": 3, "Medium": 2, "Low": 1}
    factor = sev_factors.get(report.severity, 2)
    report.priority_score = factor * (report.verification_count + 1)

    # Send verification notification alert to the original reporter
    notif_msg = f"Your reported leak '{report.title}' received another verification vote! Its priority rating has risen to {report.priority_score}."
    notif = models.Notification(user_id=report.user_id, report_id=report.id, message=notif_msg)
    db.add(notif)

    db.commit()
    db.refresh(report)

    reporter = db.query(models.User).filter(models.User.id == report.user_id).first()

    report_schema = schemas.LeakReportOut.model_validate(report)
    report_schema.reporter_name = reporter.name if reporter else "Unknown Reporter"
    return report_schema
