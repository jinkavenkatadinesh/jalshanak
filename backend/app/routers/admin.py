import shutil
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi import status as fastapi_status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.database import get_db

router = APIRouter(prefix="/admin", tags=["Admin Portal"])


@router.get("/dashboard", response_model=schemas.DashboardStats)
def get_dashboard_analytics(
    db: Session = Depends(get_db), current_admin: models.User = Depends(auth.get_current_admin)
):
    """
    Computes dashboard analytics and aggregations for administrators.
    Calculates statuses, area-wise distribution (Hyderabad-centered clusters),
    severity divisions, and captures recent activity events.
    """
    # 1. Broad totals
    total_reports = db.query(models.LeakReport).count()
    resolved_reports = db.query(models.LeakReport).filter(models.LeakReport.status == "Resolved").count()

    # Pending = Reported + Under Review + In Progress
    pending_reports = (
        db.query(models.LeakReport)
        .filter(models.LeakReport.status.in_(["Reported", "Under Review", "In Progress"]))
        .count()
    )

    # 2. Status distribution
    status_counts = (
        db.query(models.LeakReport.status, func.count(models.LeakReport.id)).group_by(models.LeakReport.status).all()
    )

    status_dist = [schemas.StatusDistribution(status=s, count=c) for s, c in status_counts]

    # 3. Severity distribution
    severity_counts = (
        db.query(models.LeakReport.severity, func.count(models.LeakReport.id))
        .group_by(models.LeakReport.severity)
        .all()
    )

    severity_dist = [schemas.SeverityDistribution(severity=s, count=c) for s, c in severity_counts]

    # 4. Area distribution (Aggregated by rounding lat/lng to 2 decimal places - approx 1.1km grid)
    # Generates a localized list of leak counts centered in Hyderabad areas
    area_groups = (
        db.query(
            func.round(models.LeakReport.latitude, 2).label("lat_bin"),
            func.round(models.LeakReport.longitude, 2).label("lng_bin"),
            func.count(models.LeakReport.id).label("count"),
        )
        .group_by("lat_bin", "lng_bin")
        .all()
    )

    area_dist = []
    for lat_bin, lng_bin, cnt in area_groups:
        # Map bins to approximate Hyderabad neighborhood names for UI flavor
        # Coordinates in Hyderabad center are around 17.38, 78.48
        area_name = "Hyderabad Central"
        l_diff = abs(lat_bin - 17.38) + abs(lng_bin - 78.48)

        if abs(lat_bin - 17.44) < 0.02 and abs(lng_bin - 78.38) < 0.02:
            area_name = "Gachibowli / Hitec City"
        elif abs(lat_bin - 17.40) < 0.02 and abs(lng_bin - 78.44) < 0.02:
            area_name = "Jubilee Hills"
        elif abs(lat_bin - 17.48) < 0.02 and abs(lng_bin - 78.55) < 0.02:
            area_name = "Secunderabad"
        elif abs(lat_bin - 17.36) < 0.02 and abs(lng_bin - 78.47) < 0.02:
            area_name = "Charminar / Old City"
        elif abs(lat_bin - 17.42) < 0.02 and abs(lng_bin - 78.50) < 0.02:
            area_name = "Begumpet"
        elif l_diff > 0.08:
            area_name = "Outer Telangana Region"
        else:
            area_name = f"Hyderabad Sector ({lat_bin}, {lng_bin})"

        area_dist.append(
            schemas.AreaDistribution(area_name=area_name, count=cnt, latitude=float(lat_bin), longitude=float(lng_bin))
        )

    # 5. Compile recent activity feed (Union reports, verifications, status changes)
    recent_activities = []

    # A. Recent reports
    reports = (
        db.query(models.LeakReport, models.User.name)
        .join(models.User, models.LeakReport.user_id == models.User.id)
        .order_by(desc(models.LeakReport.created_at))
        .limit(5)
        .all()
    )

    for r, name in reports:
        recent_activities.append(
            schemas.ActivityFeedItem(
                id=r.id,
                type="report",
                message=f"New water leak reported: '{r.title}' in Hyderabad.",
                timestamp=r.created_at,
                user_name=name,
            )
        )

    # B. Recent verifications
    verifications = (
        db.query(models.Verification, models.User.name, models.LeakReport.title)
        .join(models.User, models.Verification.user_id == models.User.id)
        .join(models.LeakReport, models.Verification.report_id == models.LeakReport.id)
        .order_by(desc(models.Verification.verified_at))
        .limit(5)
        .all()
    )

    for v, u_name, rep_title in verifications:
        recent_activities.append(
            schemas.ActivityFeedItem(
                id=v.id,
                type="verification",
                message=f"Verified the report '{rep_title}'. Credibility boosted!",
                timestamp=v.verified_at,
                user_name=u_name,
            )
        )

    # C. Recent status changes
    status_histories = (
        db.query(models.StatusHistory, models.User.name, models.LeakReport.title)
        .join(models.User, models.StatusHistory.changed_by == models.User.id)
        .join(models.LeakReport, models.StatusHistory.report_id == models.LeakReport.id)
        .order_by(desc(models.StatusHistory.changed_at))
        .limit(5)
        .all()
    )

    for sh, u_name, rep_title in status_histories:
        recent_activities.append(
            schemas.ActivityFeedItem(
                id=sh.id,
                type="status_change",
                message=f"Updated status of '{rep_title}' from {sh.old_status} to {sh.new_status}.",
                timestamp=sh.changed_at,
                user_name=u_name,
            )
        )

    # Sort everything descending by time
    recent_activities.sort(key=lambda x: x.timestamp, reverse=True)
    recent_activities = recent_activities[:10]  # Limit to 10 overall

    # 6. Calculate Water Loss & Water Saved
    # Formula: total_water_saved = sum of resolved leaks' (duration_days * daily_loss) + base 12500
    import datetime

    resolved_leaks = db.query(models.LeakReport).filter(models.LeakReport.status == "Resolved").all()
    total_water_saved = 12500
    for r in resolved_leaks:
        duration_days = (r.updated_at - r.created_at).days
        if duration_days < 1:
            duration_days = 1
        total_water_saved += duration_days * r.daily_loss

    # active_daily_loss = sum of daily_loss for all unresolved leaks
    unresolved_leaks = db.query(models.LeakReport).filter(models.LeakReport.status != "Resolved").all()
    active_daily_loss = sum(r.daily_loss for r in unresolved_leaks)

    # 7. SLA calculation
    all_reports = db.query(models.LeakReport).all()
    met_count = 0
    violated_count = 0
    now_time = datetime.datetime.utcnow()
    for r in all_reports:
        if r.status == "Resolved":
            if r.updated_at and r.expected_completion:
                if r.updated_at <= r.expected_completion:
                    met_count += 1
                else:
                    violated_count += 1
            else:
                met_count += 1
        else:
            if r.expected_completion:
                if now_time <= r.expected_completion:
                    met_count += 1
                else:
                    violated_count += 1
            else:
                met_count += 1

    total_sla_tracked = met_count + violated_count
    if total_sla_tracked > 0:
        sla_met_percent = int((met_count / total_sla_tracked) * 100)
        sla_violated_percent = 100 - sla_met_percent
    else:
        sla_met_percent = 100
        sla_violated_percent = 0

    # 8. Citizen Leaderboard
    user_counts = (
        db.query(models.User.name, func.count(models.LeakReport.id).label("count"))
        .join(models.LeakReport, models.LeakReport.user_id == models.User.id)
        .group_by(models.User.name)
        .all()
    )

    mock_users = [
        {"name": "Dinesh", "reports_count": 15, "score": 1500},
        {"name": "Ravi", "reports_count": 12, "score": 1200},
        {"name": "Akhil", "reports_count": 8, "score": 800},
    ]

    leaderboard_list = []
    for name, count in user_counts:
        if name not in ["Dinesh", "Ravi", "Akhil"]:
            leaderboard_list.append({"name": name, "reports_count": count, "score": count * 100})

    for mock in mock_users:
        leaderboard_list.append(mock)

    leaderboard_list.sort(key=lambda x: x["score"], reverse=True)

    leaderboard = []
    for idx, user_data in enumerate(leaderboard_list):
        leaderboard.append(
            schemas.LeaderboardUser(
                rank=idx + 1, name=user_data["name"], reports_count=user_data["reports_count"], score=user_data["score"]
            )
        )

    return schemas.DashboardStats(
        total_reports=total_reports,
        resolved_reports=resolved_reports,
        pending_reports=pending_reports,
        total_water_saved=total_water_saved,
        active_daily_loss=active_daily_loss,
        sla_met_percent=sla_met_percent,
        sla_violated_percent=sla_violated_percent,
        area_distribution=area_dist,
        severity_distribution=severity_dist,
        status_distribution=status_dist,
        recent_activities=recent_activities,
        leaderboard=leaderboard,
    )


@router.put("/report/{id}/status", response_model=schemas.LeakReportOut)
def update_report_status(
    id: int,
    status: str = Form(...),
    remarks: Optional[str] = Form(None),
    after_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(auth.get_current_admin),
):
    """
    Admin-only endpoint to transition leak issue statuses and log remarks.
    Validates status inputs ('Reported', 'Under Review', 'In Progress', 'Resolved').
    Supports uploading an after_image when resolving the leak.
    """
    valid_statuses = ["Reported", "Under Review", "In Progress", "Resolved"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=fastapi_status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status value. Must be one of {valid_statuses}",
        )

    report = db.query(models.LeakReport).filter(models.LeakReport.id == id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Leak report not found")

    # Record old status
    old_status = report.status
    new_status = status

    # Save the updated values
    report.status = new_status

    # Handle after_image file upload if present and status is Resolved
    if new_status == "Resolved" and after_image and after_image.filename:
        upload_dir = Path("uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_ext = Path(after_image.filename).suffix
        unique_name = f"{uuid.uuid4()}{file_ext}"
        file_path = upload_dir / unique_name

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(after_image.file, buffer)

        report.image_url_after = f"/uploads/{unique_name}"

    # Log inside Status History
    status_history_log = models.StatusHistory(
        report_id=id, old_status=old_status, new_status=new_status, remarks=remarks, changed_by=current_admin.id
    )
    db.add(status_history_log)

    # Generate a Notification entry for the reporter if status changed
    if old_status != new_status:
        notif_msg = f"The status of your reported leak '{report.title}' has been updated to '{new_status}'."
        if new_status == "Resolved":
            notif_msg = f"Your reported leak '{report.title}' has been successfully resolved. Thank you for your civic contribution!"

        notif = models.Notification(user_id=report.user_id, report_id=report.id, message=notif_msg)
        db.add(notif)

    db.commit()
    db.refresh(report)

    reporter = db.query(models.User).filter(models.User.id == report.user_id).first()

    report_schema = schemas.LeakReportOut.model_validate(report)
    report_schema.reporter_name = reporter.name if reporter else "Unknown Reporter"
    return report_schema


@router.get("/report/{id}/history", response_model=List[schemas.StatusHistoryOut])
def get_report_status_history(id: int, db: Session = Depends(get_db)):
    """
    Fetches the historical comments and state log transitions for a specific leak report.
    """
    history_logs = (
        db.query(
            models.StatusHistory.id,
            models.StatusHistory.report_id,
            models.StatusHistory.old_status,
            models.StatusHistory.new_status,
            models.StatusHistory.remarks,
            models.StatusHistory.changed_by,
            models.StatusHistory.changed_at,
            models.User.name.label("changed_by_name"),
        )
        .join(models.User, models.StatusHistory.changed_by == models.User.id)
        .filter(models.StatusHistory.report_id == id)
        .order_by(desc(models.StatusHistory.changed_at))
        .all()
    )

    history_list = []
    for h in history_logs:
        history_list.append(
            schemas.StatusHistoryOut(
                id=h.id,
                report_id=h.report_id,
                old_status=h.old_status,
                new_status=h.new_status,
                remarks=h.remarks,
                changed_by=h.changed_by,
                changed_by_name=h.changed_by_name,
                changed_at=h.changed_at,
            )
        )
    return history_list
