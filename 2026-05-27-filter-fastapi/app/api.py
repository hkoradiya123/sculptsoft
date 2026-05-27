from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session
from .repository import (
    create_person,
    delete_person,
    get_person,
    list_persons,
    update_person,
)
from .schemas import PageResponse, PersonCreate, PersonOut, PersonUpdate

router = APIRouter(prefix="/persons", tags=["persons"])


@router.post("", response_model=PersonOut, status_code=201)
async def create(payload: PersonCreate, session: AsyncSession = Depends(get_session)):
    return await create_person(session, payload)


@router.get("/{person_id}", response_model=PersonOut)
async def get_by_id(
    person_id: int, session: AsyncSession = Depends(get_session)
):
    person = await get_person(session, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.put("/{person_id}", response_model=PersonOut)
async def update(
    person_id: int,
    payload: PersonUpdate,
    session: AsyncSession = Depends(get_session),
):
    person = await update_person(session, person_id, payload)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.delete("/{person_id}", status_code=204)
async def remove(person_id: int, session: AsyncSession = Depends(get_session)):
    deleted = await delete_person(session, person_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Person not found")
    return None


@router.get("", response_model=PageResponse)
async def list_all(
    page: int = 1,
    limit: int = 10,
    columns: Optional[str] = None,
    sort: Optional[str] = None,
    filters: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    return await list_persons(session, page, limit, columns, sort, filters)
