from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.schemas.user import UserProfile, UserProfileUpdate
from app.services import user_service

router = APIRouter()

@router.get("/", response_model=UserProfile)
def read_profile(
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get current user profile."""
    profile = user_service.get_user_profile(db, user_id=current_user.id)
    if not profile:
        # Create empty profile if none exists
        profile = user_service.update_user_profile(db, current_user.id, UserProfileUpdate())
    return profile

@router.put("/", response_model=UserProfile)
def update_profile(
    *,
    db: Session = Depends(deps.get_db),
    profile_in: UserProfileUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Update user profile."""
    profile = user_service.update_user_profile(db, user_id=current_user.id, profile_in=profile_in)
    return profile
