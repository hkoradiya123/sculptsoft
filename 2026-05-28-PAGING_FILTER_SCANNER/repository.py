from math import ceil

from fastapi import HTTPException
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from models import Person

# =====================================================
# ALLOWED COLUMNS
# =====================================================

ALLOWED_COLUMNS = {
    "id",
    "name",
    "age",
    "country",
}


# =====================================================
# VALIDATE COLUMN
# =====================================================

def validate_column(column: str):
    if column not in ALLOWED_COLUMNS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid column: {column}"
        )


# =====================================================
# PARSE FILTERS
# country:USA,name:ali
# =====================================================

def parse_filters(filters: str | None):
    filter_map = {}

    if not filters:
        return filter_map

    pairs = filters.split(",")

    for pair in pairs:
        if ":" not in pair:
            continue

        key, value = pair.split(":", 1)

        key = key.strip()
        value = value.strip()

        validate_column(key)

        filter_map[key] = value

    return filter_map


# =====================================================
# APPLY FILTERS
# =====================================================

def apply_filters(query, filter_map):
    for key, value in filter_map.items():
        column = getattr(Person, key)
        query = query.filter(
            column.ilike(f"%{value}%")
        )

    return query


# =====================================================
# APPLY SEARCH
# =====================================================

def apply_search(query, search: str | None):
    if not search:
        return query

    query = query.filter(
        or_(
            Person.name.ilike(f"%{search}%"),
            Person.country.ilike(f"%{search}%")
        )
    )

    return query


# =====================================================
# APPLY SORT
# =====================================================

def apply_sort(query, sort: str | None):
    if not sort:
        return query

    sort_columns = [
        col.strip()
        for col in sort.split(",")
        if col.strip()
    ]

    for col in sort_columns:
        # Reject malformed syntax
        if col.count("-") > 1:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort syntax: {col}"
            )

        # DESCENDING CHECK
        is_descending = col.startswith("-")

        # CLEAN COLUMN
        clean_col = (
            col[1:]
            if is_descending
            else col
        )

        # VALIDATE
        validate_column(clean_col)

        # GET COLUMN ATTRIBUTE
        column_attr = getattr(Person, clean_col)

        # APPLY SORT
        query = query.order_by(
            desc(column_attr)
            if is_descending
            else asc(column_attr)
        )

    return query


# =====================================================
# CREATE PERSON
# =====================================================

def create_person(
    db: Session,
    name: str,
    age: int,
    country: str,
):
    person = Person(
        name=name,
        age=age,
        country=country,
    )

    db.add(person)
    db.commit()
    db.refresh(person)

    return person


# =====================================================
# GET PERSONS
# =====================================================

def get_persons(
    db: Session,
    page: int = 1,
    limit: int = 5,
    sort: str | None = None,
    filters: str | None = None,
    search: str | None = None,
):
    # -----------------------------------
    # VALIDATION
    # -----------------------------------

    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be >= 1"
        )

    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Limit must be >= 1"
        )

    # -----------------------------------
    # BASE QUERY
    # -----------------------------------

    query = db.query(Person)

    # -----------------------------------
    # FILTERS
    # -----------------------------------

    filter_map = parse_filters(filters)

    query = apply_filters(
        query,
        filter_map
    )

    # -----------------------------------
    # SEARCH
    # -----------------------------------

    query = apply_search(
        query,
        search
    )

    # -----------------------------------
    # TOTAL RECORDS
    # -----------------------------------

    total_records = query.count()

    # -----------------------------------
    # TOTAL PAGES
    # -----------------------------------

    total_pages = (
        ceil(total_records / limit)
        if total_records
        else 0
    )

    # -----------------------------------
    # SORTING
    # -----------------------------------

    query = apply_sort(
        query,
        sort
    )

    # -----------------------------------
    # PAGINATION
    # -----------------------------------

    offset = (page - 1) * limit

    persons = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    # -----------------------------------
    # RESPONSE
    # -----------------------------------

    return {
        "page_number": page,
        "page_size": limit,
        "total_pages": total_pages,
        "total_records": total_records,
        "content": [
            {
                "id": p.id,
                "name": p.name,
                "age": p.age,
                "country": p.country,
            }
            for p in persons
        ]
    }
