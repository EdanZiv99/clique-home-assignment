import csv
from typing import Optional

from checkin_tool.models import Member


def load_members(path: str) -> list[Member]:
    members = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            channel = row["preferred_channel"].strip() or None
            flags = [f.strip() for f in row["risk_flags"].strip().split(";")] if row["risk_flags"].strip() else []

            members.append(Member(
                member_id=row["member_id"].strip(),
                full_name=row["full_name"].strip(),
                age=int(row["age"]),
                preferred_channel=channel,
                recent_discharge="recent_discharge" in flags,
                lives_alone="lives_alone" in flags,
            ))

    return members
