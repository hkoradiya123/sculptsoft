from __future__ import annotations

from math import ceil
from typing import Dict, Iterable, List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Person
from .schemas import PageResponse, PersonCreate, PersonUpdate

ALLOWED_COLUMNS = {"id", "name", "country", "age", "sex"}


def _parse_columns(columns: Optional[str]) -> Optional[List[str]]:
    if not columns:
        return None
    parsed = [item.strip() for item in columns.split(",") if item.strip()]
    if not parsed:
        return None
    for col in parsed:
        if col not in ALLOWED_COLUMNS:
            raise HTTPException(status_code=400, detail=f"Invalid column: {col}")
    return parsed


def _parse_sort(sort: Optional[str]) -> List[Tuple[str, bool]]:
    if not sort:
        return []
    parsed: List[Tuple[str, bool]] = []
    for raw in sort.split(","):
        raw = raw.strip()
        if not raw:
            continue
        desc = raw.startswith("-")
        col = raw[1:] if desc else raw
        if col not in ALLOWED_COLUMNS:
            raise HTTPException(status_code=400, detail=f"Invalid sort column: {col}")
        parsed.append((col, desc))
    return parsed


def _parse_filters(filters: Optional[str]) -> Dict[str, str]:
    if not filters:
        return {}
    parsed: Dict[str, str] = {}
    for pair in filters.split(","):
        pair = pair.strip()
        if not pair:
            continue
        if ":" not in pair:
            raise HTTPException(status_code=400, detail="Invalid filter format")
        key, value = pair.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            raise HTTPException(status_code=400, detail="Invalid filter format")
        if key not in ALLOWED_COLUMNS:
            raise HTTPException(status_code=400, detail=f"Invalid filter column: {key}")
        parsed[key] = value
    return parsed


def _apply_filters(query: Select, filters: Dict[str, str]) -> Select:
    for col, value in filters.items():
        column = getattr(Person, col)
        query = query.where(column.like(f"%{value}%"))
    return query


def _apply_sort(query: Select, sort: Iterable[Tuple[str, bool]]) -> Select:
    for col, desc in sort:
        column = getattr(Person, col)
        query = query.order_by(column.desc() if desc else column.asc())
    return query


async def create_person(session: AsyncSession, payload: PersonCreate) -> Person:
    person = Person(**payload.dict())
    session.add(person)
    await session.commit()
    await session.refresh(person)
    return person


async def get_person(session: AsyncSession, person_id: int) -> Optional[Person]:
    result = await session.execute(select(Person).where(Person.id == person_id))
    return result.scalar_one_or_none()


async def update_person(
    session: AsyncSession, person_id: int, payload: PersonUpdate
) -> Optional[Person]:
    person = await get_person(session, person_id)
    if not person:
        return None
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(person, key, value)
    await session.commit()
    await session.refresh(person)
    return person


async def delete_person(session: AsyncSession, person_id: int) -> bool:
    person = await get_person(session, person_id)
    if not person:
        return False
    await session.delete(person)
    await session.commit()
    return True


async def list_persons(
    session: AsyncSession,
    page: int,
    limit: int,
    columns: Optional[str],
    sort: Optional[str],
    filters: Optional[str],
) -> PageResponse:
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    if limit < 1:
        raise HTTPException(status_code=400, detail="Limit must be >= 1")

    selected_columns = _parse_columns(columns)
    sort_columns = _parse_sort(sort)
    filter_map = _parse_filters(filters)

    base_query = select(Person)
    base_query = _apply_filters(base_query, filter_map)

    count_query = select(func.count()).select_from(Person)
    count_query = _apply_filters(count_query, filter_map)
    total_records = (await session.execute(count_query)).scalar_one()
    total_pages = ceil(total_records / limit) if total_records else 0

    if selected_columns:
        column_objs = [getattr(Person, col) for col in selected_columns]
        query = select(*column_objs)
    else:
        query = base_query

    query = _apply_filters(query, filter_map)
    query = _apply_sort(query, sort_columns)
    query = query.offset((page - 1) * limit).limit(limit)

    result = await session.execute(query)

    if selected_columns:
        rows = result.all()
        content = [dict(zip(selected_columns, row)) for row in rows]
    else:
        content = result.scalars().all()

    return PageResponse(
        page_number=page,
        page_size=limit,
        total_pages=total_pages,
        total_records=total_records,
        content=content,
    )
