from sqlalchemy.orm import Session
from app.models.user import User, UserProfile
from app.schemas.user import UserCreate, UserProfileUpdate
from app.core.security import get_password_hash
from app.core.exceptions import BadRequestException

def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_in: UserCreate) -> User:
    user = get_user_by_email(db, user_in.email)
    if user:
        raise BadRequestException(detail="Email already registered")
    
    hashed_password = get_password_hash(user_in.password)
    db_user = User(email=user_in.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_profile(db: Session, user_id: int, profile_in: UserProfileUpdate) -> UserProfile:
    db_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not db_profile:
        db_profile = UserProfile(user_id=user_id)
        db.add(db_profile)
    
    profile_data = profile_in.model_dump(exclude_unset=True)
    for key, value in profile_data.items():
        setattr(db_profile, key, value)
        
    db.commit()
    db.refresh(db_profile)
    return db_profile

def get_user_profile(db: Session, user_id: int) -> UserProfile:
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
