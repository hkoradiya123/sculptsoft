#!/usr/bin/env python3
"""Migrate Firebase Auth users and Firestore collections into MongoDB.

Usage:
  python migrate_firestore_to_mongo.py
  python migrate_firestore_to_mongo.py --email user@example.com
  python migrate_firestore_to_mongo.py --collections users,performance_logs
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import firebase_admin
from firebase_admin import auth, credentials, firestore
from dotenv import load_dotenv
from pymongo import MongoClient

DEFAULT_COLLECTIONS = [
    "users",
    "payments",
    "performance_logs",
    "notifications",
    "finance_transactions",
    "admin_chat_messages",
    "matches",
    "match_players",
    "ball_events",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migrate Firebase Auth and Firestore data to MongoDB",
    )
    parser.add_argument(
        "--collections",
        default=",".join(DEFAULT_COLLECTIONS),
        help="Comma-separated Firestore collection names to migrate",
    )
    parser.add_argument(
        "--email",
        default="",
        help="Migrate only this user by email (for users and auth users)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without writing to MongoDB",
    )
    return parser.parse_args()


def load_environment(script_dir: Path) -> None:
    env_path = script_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)


def init_firebase(script_dir: Path) -> None:
    if firebase_admin._apps:
        return

    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "firebase-service-account.json").strip()

    if service_account_json:
        cred = credentials.Certificate(json.loads(service_account_json))
        firebase_admin.initialize_app(cred)
        return

    cred_path = Path(service_account_path)
    if not cred_path.is_absolute():
        cred_path = script_dir / cred_path

    if not cred_path.exists():
        raise FileNotFoundError(f"Service account file not found: {cred_path}")

    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(cred)


def get_mongo() -> tuple[MongoClient, str]:
    mongo_uri = os.getenv("MONGODB_URI", "").strip()
    db_name = os.getenv("MONGODB_DB_NAME", "ssc").strip() or "ssc"

    if not mongo_uri:
        raise RuntimeError("MONGODB_URI is required in backend/.env")

    client = MongoClient(mongo_uri, tz_aware=True, serverSelectionTimeoutMS=10000)
    client.admin.command("ping")
    return client, db_name


def to_serializable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

    if hasattr(value, "path"):
        return str(value.path)

    if isinstance(value, dict):
        return {k: to_serializable(v) for k, v in value.items()}

    if isinstance(value, list):
        return [to_serializable(v) for v in value]

    return value


def migrate_auth_users(mongo_db, email_filter: str, dry_run: bool) -> int:
    auth_collection = mongo_db["firebase_auth_users"]
    users_collection = mongo_db["users"]

    migrated = 0
    for user in auth.list_users().iterate_all():
        if email_filter and user.email != email_filter:
            continue

        payload = {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "phone_number": user.phone_number,
            "email_verified": user.email_verified,
            "disabled": user.disabled,
            "provider_data": [
                {
                    "uid": p.uid,
                    "provider_id": p.provider_id,
                    "email": p.email,
                    "display_name": p.display_name,
                }
                for p in (user.provider_data or [])
            ],
            "created_at": datetime.fromtimestamp(user.user_metadata.creation_timestamp / 1000, tz=timezone.utc)
            if user.user_metadata and user.user_metadata.creation_timestamp
            else None,
            "last_sign_in_at": datetime.fromtimestamp(user.user_metadata.last_sign_in_timestamp / 1000, tz=timezone.utc)
            if user.user_metadata and user.user_metadata.last_sign_in_timestamp
            else None,
            "source": "firebase_auth",
        }

        if not dry_run:
            auth_collection.update_one({"uid": user.uid}, {"$set": payload}, upsert=True)

            if user.email:
                users_collection.update_one(
                    {"email": user.email},
                    {"$set": {"uid": user.uid, "firebase_email_verified": user.email_verified}},
                    upsert=False,
                )

        migrated += 1

    return migrated


def migrate_firestore_collections(mongo_db, collections: list[str], email_filter: str, dry_run: bool) -> dict[str, int]:
    db = firestore.client()
    stats: dict[str, int] = {}

    for collection_name in collections:
        target = mongo_db[collection_name]
        count = 0

        for snap in db.collection(collection_name).stream():
            data = snap.to_dict() or {}
            payload = to_serializable(data)

            if "id" not in payload:
                payload["id"] = int(snap.id) if snap.id.isdigit() else snap.id

            payload["_doc_id"] = snap.id
            payload["_source"] = "firestore"

            if email_filter and collection_name == "users" and payload.get("email") != email_filter:
                continue

            if not dry_run:
                target.update_one({"id": payload["id"]}, {"$set": payload}, upsert=True)

            count += 1

        stats[collection_name] = count

    return stats


def main() -> None:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent

    load_environment(script_dir)
    init_firebase(script_dir)
    mongo_client, db_name = get_mongo()

    mongo_db = mongo_client[db_name]
    collections = [item.strip() for item in args.collections.split(",") if item.strip()]

    print("=" * 72)
    print("FIRESTORE -> MONGODB MIGRATION")
    print("=" * 72)
    print(f"Mongo DB: {db_name}")
    print(f"Collections: {', '.join(collections)}")
    if args.email:
        print(f"Email filter: {args.email}")
    print(f"Dry run: {args.dry_run}")

    auth_count = migrate_auth_users(mongo_db, args.email, args.dry_run)
    collection_stats = migrate_firestore_collections(mongo_db, collections, args.email, args.dry_run)

    print("\nMigration complete")
    print("-" * 72)
    print(f"Firebase Auth users migrated: {auth_count}")
    for name, count in collection_stats.items():
        print(f"Firestore collection {name}: {count} docs")


if __name__ == "__main__":
    main()
