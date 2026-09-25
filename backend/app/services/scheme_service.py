from sqlalchemy.orm import Session
from app.models.scheme import Scheme
from app.schemas.scheme import SchemeCreate, SchemeUpdate
from app.core.exceptions import NotFoundException

def get_scheme(db: Session, scheme_id: int) -> Scheme:
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise NotFoundException(detail="Scheme not found")
    return scheme

def get_schemes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Scheme).offset(skip).limit(limit).all()

def create_scheme(db: Session, scheme_in: SchemeCreate) -> Scheme:
    db_scheme = Scheme(**scheme_in.model_dump())
    db.add(db_scheme)
    db.commit()
    db.refresh(db_scheme)
    return db_scheme

def update_scheme(db: Session, scheme_id: int, scheme_in: SchemeUpdate) -> Scheme:
    db_scheme = get_scheme(db, scheme_id)
    update_data = scheme_in.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_scheme, key, value)
        
    db.commit()
    db.refresh(db_scheme)
    return db_scheme

def disable_scheme(db: Session, scheme_id: int) -> Scheme:
    db_scheme = get_scheme(db, scheme_id)
    db_scheme.is_active = False
    db.commit()
    db.refresh(db_scheme)
    return db_scheme
