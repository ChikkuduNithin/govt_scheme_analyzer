from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.schemas.scheme import Scheme, SchemeCreate, SchemeUpdate
from app.services import scheme_service

router = APIRouter()

@router.get("/", response_model=List[Scheme])
def read_schemes(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve schemes."""
    schemes = scheme_service.get_schemes(db, skip=skip, limit=limit)
    return schemes

@router.get("/{scheme_id}", response_model=Scheme)
def read_scheme(
    scheme_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get scheme by ID."""
    return scheme_service.get_scheme(db, scheme_id=scheme_id)

@router.post("/", response_model=Scheme)
def create_scheme(
    *,
    db: Session = Depends(deps.get_db),
    scheme_in: SchemeCreate,
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """Create new scheme (Admin only)."""
    return scheme_service.create_scheme(db, scheme_in=scheme_in)

@router.put("/{scheme_id}", response_model=Scheme)
def update_scheme(
    *,
    db: Session = Depends(deps.get_db),
    scheme_id: int,
    scheme_in: SchemeUpdate,
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """Update scheme (Admin only)."""
    return scheme_service.update_scheme(db, scheme_id=scheme_id, scheme_in=scheme_in)

@router.delete("/{scheme_id}", response_model=Scheme)
def disable_scheme(
    *,
    db: Session = Depends(deps.get_db),
    scheme_id: int,
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """Disable scheme (Admin only)."""
    return scheme_service.disable_scheme(db, scheme_id=scheme_id)
