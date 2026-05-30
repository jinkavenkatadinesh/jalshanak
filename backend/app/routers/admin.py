import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/admin", tags=["Admin Portal"])

@router.get("/dashboard", response_model=schemas.DashboardStats)
def get_dashboard_analytics(
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(auth.get_current_admin)
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
    pending_reports = db.query(models.LeakReport).filter(
        models.LeakReport.status.in_(["Reported", "Under Review", "In Progress"])
    ).count()

    # 2. Status distribution
    status_counts = db.query(
        models.LeakReport.status,
        func.count(models.LeakReport.id)
    ).group_by(models.LeakReport.status).all()
    
    status_dist = [
        schemas.StatusDistribution(status=s, count=c) for s, c in status_counts
    ]

    # 3. Severity distribution
    severity_counts = db.query(
        models.LeakReport.severity,
        func.count(models.LeakReport.id)
    ).group_by(models.LeakReport.severity).all()
    
    severity_dist = [
        schemas.SeverityDistribution(severity=s, count=c) for s, c in severity_counts
    ]

    # 4. Area distribution (Aggregated by rounding lat/lng to 2 decimal places - approx 1.1km grid)
    # Generates a localized list of leak counts centered in Hyderabad areas
    area_groups = db.query(
        func.round(models.LeakReport.latitude, 2).label("lat_bin"),
        func.round(models.LeakReport.longitude, 2).label("lng_bin"),
        func.count(models.LeakReport.id).label("count")
    ).group_by("lat_bin", "lng_bin").all()

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
            schemas.AreaDistribution(
                area_name=area_name,
                count=cnt,
                latitude=float(lat_bin),
                longitude=float(lng_bin)
            )
        )

    # 5. Compile recent activity feed (Union reports, verifications, status changes)
    recent_activities = []
    
    # A. Recent reports
    reports = db.query(models.LeakReport, models.User.name).join(
        models.User, models.LeakReport.user_id == models.User.id
    ).order_by(desc(models.LeakReport.created_at)).limit(5).all()
    
    for r, name in reports:
        recent_activities.append(
            schemas.ActivityFeedItem(
                id=r.id,
                type="report",
                message=f"New water leak reported: '{r.title}' in Hyderabad.",
                timestamp=r.created_at,
                user_name=name
            )
        )

    # B. Recent verifications
    verifications = db.query(models.Verification, models.User.name, models.LeakReport.title).join(
        models.User, models.Verification.user_id == models.User.id
    ).join(
        models.LeakReport, models.Verification.report_id == models.LeakReport.id
    ).order_by(desc(models.Verification.verified_at)).limit(5).all()
    
    for v, u_name, rep_title in verifications:
        recent_activities.append(
            schemas.ActivityFeedItem(
                id=v.id,
                type="verification",
                message=f"Verified the report '{rep_title}'. Credibility boosted!",
                timestamp=v.verified_at,
                user_name=u_name
            )
        )

    # C. Recent status changes
    status_histories = db.query(
        models.StatusHistory, 
        models.User.name, 
        models.LeakReport.title
    ).join(
        models.User, models.StatusHistory.changed_by == models.User.id
    ).join(
        models.LeakReport, models.StatusHistory.report_id == models.LeakReport.id
    ).order_by(desc(models.StatusHistory.changed_at)).limit(5).all()
    
    for sh, u_name, rep_title in status_histories:
        recent_activities.append(
            schemas.ActivityFeedItem(
                id=sh.id,
                type="status_change",
                message=f"Updated status of '{rep_title}' from {sh.old_status} to {sh.new_status}.",
                timestamp=sh.changed_at,
                user_name=u_name
            )
        )

    # Sort everything descending by time
    recent_activities.sort(key=lambda x: x.timestamp, reverse=True)
    recent_activities = recent_activities[:10]  # Limit to 10 overall

    return schemas.DashboardStats(
        total_reports=total_reports,
        resolved_reports=resolved_reports,
        pending_reports=pending_reports,
        area_distribution=area_dist,
        severity_distribution=severity_dist,
        status_distribution=status_dist,
        recent_activities=recent_activities
    )

@router.put("/report/{id}/status", response_model=schemas.LeakReportOut)
def update_report_status(
    id: int,
    status_in: schemas.StatusUpdate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(auth.get_current_admin)
):
    """
    Admin-only endpoint to transition leak issue statuses and log remarks.
    Validates status inputs ('Reported', 'Under Review', 'In Progress', 'Resolved').
    """
    valid_statuses = ["Reported", "Under Review", "In Progress", "Resolved"]
    if status_in.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status value. Must be one of {valid_statuses}"
        )
        
    report = db.query(models.LeakReport).filter(models.LeakReport.id == id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Leak report not found")
        
    # Record old status
    old_status = report.status
    new_status = status_in.status
    
    # Save the updated values
    report.status = new_status
    
    # Log inside Status History
    status_history_log = models.StatusHistory(
        report_id=id,
        old_status=old_status,
        new_status=new_status,
        remarks=status_in.remarks,
        changed_by=current_admin.id
    )
    db.add(status_history_log)
    db.commit()
    db.refresh(report)
    
    reporter = db.query(models.User).filter(models.User.id == report.user_id).first()
    
    report_schema = schemas.LeakReportOut.model_validate(report)
    report_schema.reporter_name = reporter.name if reporter else "Unknown Reporter"
    return report_schema

@router.get("/report/{id}/history", response_model=List[schemas.StatusHistoryOut])
def get_report_status_history(
    id: int,
    db: Session = Depends(get_db)
):
    """
    Fetches the historical comments and state log transitions for a specific leak report.
    """
    history_logs = db.query(
        models.StatusHistory.id,
        models.StatusHistory.report_id,
        models.StatusHistory.old_status,
        models.StatusHistory.new_status,
        models.StatusHistory.remarks,
        models.StatusHistory.changed_by,
        models.StatusHistory.changed_at,
        models.User.name.label("changed_by_name")
    ).join(
        models.User, models.StatusHistory.changed_by == models.User.id
    ).filter(
        models.StatusHistory.report_id == id
    ).order_by(desc(models.StatusHistory.changed_at)).all()
    
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
                changed_at=h.changed_at
            )
        )
    return history_list
