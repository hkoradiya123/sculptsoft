from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from repository import (
    create_person,
    get_persons,
)
from schemas import PersonCreate

router = APIRouter()


# =====================================================
# CREATE PERSON
# =====================================================

@router.post("/persons")
def create_person_api(
    payload: PersonCreate,
    db: Session = Depends(get_db),
):
    return create_person(
        db=db,
        name=payload.name,
        age=payload.age,
        country=payload.country,
    )


# =====================================================
# GET PERSONS
# =====================================================

@router.get("/persons")
def get_persons_api(
    page: int = 1,
    limit: int = 5,
    sort: str | None = None,
    filters: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    return get_persons(
        db=db,
        page=page,
        limit=limit,
        sort=sort,
        filters=filters,
        search=search,
    )
