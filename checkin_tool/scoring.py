from datetime import date
from typing import Optional

from checkin_tool.models import ContactRecord, Member


def calculate_score(member: Member, contact: Optional[ContactRecord], today: date) -> float:
    score = 0.0

    if member.recent_discharge:
        score += 3
    if member.lives_alone:
        score += 2
    if member.age >= 80:
        score += 1
    if contact is not None and contact.outcome == "no_answer":
        score += 1

    days_since_contact = (today - contact.last_contact_date).days if contact is not None else 0
    score += days_since_contact / 7

    return score
