import csv
import json
import sys
from datetime import date, datetime
from typing import Optional

from checkin_tool.models import ContactRecord, Member


def load_members(path: str) -> list[Member]:
    members = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):
            try:
                # Normalize preferred_channel (empty -> None)
                channel = row["preferred_channel"].strip() or None
                # Convert semicolon-separated string into clean list of flags
                flags = [f.strip() for f in row["risk_flags"].strip().split(";")] if row["risk_flags"].strip() else []

                members.append(Member(
                    member_id=row["member_id"].strip(),
                    full_name=row["full_name"].strip(),
                    age=int(row["age"]),
                    preferred_channel=channel,
                    recent_discharge="recent_discharge" in flags,
                    lives_alone="lives_alone" in flags,
                ))
            except (ValueError, KeyError) as e:
                print(f"[WARNING] Skipping row {row_num} in {path}: {e}", file=sys.stderr)

    return members


def load_contacts(path: str) -> dict[str, ContactRecord]:
    contacts = {}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):
            try:
                member_id = row["member_id"].strip()
                record = ContactRecord(
                    member_id=member_id,
                    last_contact_date=datetime.strptime(row["last_contact_date"].strip(), "%Y-%m-%d").date(),
                    outcome=row["outcome"].strip().lower(),
                )
                # Update contact record if it's newer or doesn't exist
                if member_id not in contacts or record.last_contact_date > contacts[member_id].last_contact_date:
                    contacts[member_id] = record
            except (ValueError, KeyError) as e:
                print(f"[WARNING] Skipping row {row_num} in {path}: {e}", file=sys.stderr)

    return contacts


def load_holidays(path: str) -> set[date]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    return {datetime.strptime(d.strip(), "%Y-%m-%d").date() for d in raw}
