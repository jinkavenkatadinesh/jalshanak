import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# --- Auth Schemas ---


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: Optional[str] = "citizen"  # 'citizen' or 'admin'


class UserOut(UserBase):
    id: int
    role: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None


# --- Leak Report Schemas ---


class LeakReportCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    latitude: float
    longitude: float


class LeakReportOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    latitude: float
    longitude: float
    status: str
    verification_count: int
    severity: str
    image_url_after: Optional[str] = None
    priority_score: int
    daily_loss: int
    assigned_engineer: Optional[str] = None
    assigned_date: Optional[datetime.datetime] = None
    expected_completion: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    reporter_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --- Verification Schemas ---


class VerificationCreate(BaseModel):
    report_id: int


class VerificationOut(BaseModel):
    id: int
    report_id: int
    user_id: int
    verified_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# --- Status History Schemas ---


class StatusHistoryOut(BaseModel):
    id: int
    report_id: int
    old_status: str
    new_status: str
    remarks: Optional[str] = None
    changed_by: int
    changed_by_name: Optional[str] = None
    changed_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class StatusUpdate(BaseModel):
    status: str = Field(..., description="Must be one of 'Reported', 'In Progress', 'Resolved'")
    remarks: Optional[str] = None


class NotificationOut(BaseModel):
    id: int
    user_id: int
    report_id: int
    message: str
    is_read: int  # 0 for unread, 1 for read
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# --- Analytics & Dashboard Schemas ---


class AreaDistribution(BaseModel):
    area_name: str
    count: int
    latitude: float
    longitude: float


class SeverityDistribution(BaseModel):
    severity: str
    count: int


class StatusDistribution(BaseModel):
    status: str
    count: int


class ActivityFeedItem(BaseModel):
    id: int
    type: str  # 'report', 'status_change', 'verification'
    message: str
    timestamp: datetime.datetime
    user_name: str


class LeaderboardUser(BaseModel):
    rank: int
    name: str
    reports_count: int
    score: int


class DashboardStats(BaseModel):
    total_reports: int
    resolved_reports: int
    pending_reports: int  # Reported + In Progress
    total_water_saved: int
    active_daily_loss: int
    sla_met_percent: int
    sla_violated_percent: int
    area_distribution: List[AreaDistribution]
    severity_distribution: List[SeverityDistribution]
    status_distribution: List[StatusDistribution]
    recent_activities: List[ActivityFeedItem]
    leaderboard: List[LeaderboardUser]
