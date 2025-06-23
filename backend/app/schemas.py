from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class EmailRequest(BaseModel):
    email: EmailStr
    force_refresh: Optional[bool] = False

class EmailResponse(BaseModel):
    status: str
    source: str  # "cache" или "fresh"
    data: Dict[str, Any]

class BulkSearchResponse(BaseModel):
    total: int
    processed: int
    existing: int
    new: int
    invalid: int
    results: List[Dict[str, Any]]

class ProfileResponse(BaseModel):
    status: str
    data: Dict[str, Any]

class SearchHistoryItem(BaseModel):
    email: str
    search_type: str
    results_found: int
    created_at: datetime

class StatsResponse(BaseModel):
    total_profiles: int
    total_searches: int
    recent_searches: List[Dict[str, Any]]

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    details: Optional[str] = None

# Схемы для данных профиля
class SocialProfile(BaseModel):
    platform: str
    url: str
    username: Optional[str] = None
    followers: Optional[int] = None
    verified: Optional[bool] = None

class PersonInfo(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    occupation: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class EmailProfileData(BaseModel):
    email: str
    person_info: Optional[PersonInfo] = None
    social_profiles: List[SocialProfile] = []
    websites: List[str] = []
    phone_numbers: List[str] = []
    addresses: List[str] = []
    sources: List[str] = []
    confidence_score: Optional[float] = None
    last_updated: datetime
    
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str = "1.0.0"

