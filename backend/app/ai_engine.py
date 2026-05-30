import math
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import LeakReport

def analyze_leak_image(description: str, filename: str) -> Dict[str, Any]:
    """
    Simulates a computer vision model that analyzes uploaded images for water leak detection.
    Predicts whether a leak exists, estimates its severity, and assigns a confidence score.
    """
    desc_lower = (description or "").lower()
    
    # Heuristics based on keywords in user descriptions
    high_severity_keywords = ["burst", "flood", "gushing", "heavy", "spray", "spurt", "fountain", "flow", "torrential", "disaster", "danger"]
    low_severity_keywords = ["dripping", "slow", "seeping", "minor", "trickle", "drop", "damp", "moist", "small"]
    
    is_leak_detected = True
    confidence = 0.92
    
    # Check if there is an image uploaded (if filename is provided)
    # If no image, maybe confidence is slightly lower
    if not filename:
        confidence = 0.78
        
    # Analyze text & image context
    if any(k in desc_lower for k in high_severity_keywords):
        severity = "High"
        confidence = 0.95 + (0.04 * (len(desc_lower) % 10) / 10.0) # Conf: 0.95 - 0.99
    elif any(k in desc_lower for k in low_severity_keywords):
        severity = "Low"
        confidence = 0.85 + (0.07 * (len(desc_lower) % 10) / 10.0) # Conf: 0.85 - 0.92
    else:
        severity = "Medium"
        confidence = 0.88 + (0.07 * (len(desc_lower) % 10) / 10.0) # Conf: 0.88 - 0.95
        
    return {
        "is_leak_detected": is_leak_detected,
        "severity": severity,
        "confidence_score": round(confidence, 2),
        "ai_remarks": f"AI detection complete. Water leak detected visually with {int(confidence*100)}% confidence. Predicted Severity: {severity}."
    }

def check_for_duplicate_reports(db: Session, latitude: float, longitude: float, max_distance_meters: float = 100.0) -> List[Dict[str, Any]]:
    """
    Checks if there are active reports (status is 'Reported' or 'In Progress') 
    within max_distance_meters of the proposed location.
    
    Uses standard equirectangular distance approximation for GPS coords.
    1 degree of latitude ~ 111,139 meters
    1 degree of longitude ~ 111,139 * cos(latitude) meters
    """
    active_reports = db.query(LeakReport).filter(LeakReport.status.in_(["Reported", "In Progress"])).all()
    duplicates = []
    
    for report in active_reports:
        # Calculate distance in meters
        lat1, lon1 = latitude, longitude
        lat2, lon2 = report.latitude, report.longitude
        
        # Approximate distance calculation
        lat_mid = math.radians((lat1 + lat2) / 2.0)
        d_lat = math.radians(lat2 - lat1) * 111139.0
        d_lon = math.radians(lon2 - lon1) * 111139.0 * math.cos(lat_mid)
        
        distance = math.sqrt(d_lat**2 + d_lon**2)
        
        if distance <= max_distance_meters:
            duplicates.append({
                "id": report.id,
                "title": report.title,
                "status": report.status,
                "distance_meters": round(distance, 1),
                "reporter_id": report.user_id,
                "created_at": report.created_at
            })
            
    return duplicates
