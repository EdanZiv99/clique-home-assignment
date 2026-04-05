from datetime import date

from checkin_tool.eligibility import is_eligible
from checkin_tool.loader import load_contacts, load_holidays, load_members
from checkin_tool.models import CheckInCandidate
from checkin_tool.scoring import calculate_score


def get_candidates(
    members_path: str,
    contacts_path: str,
    holidays_path: str,
    top_n: int,
    today: date,
) -> list[CheckInCandidate]:
    members = load_members(members_path)
    contacts = load_contacts(contacts_path)
    holidays = load_holidays(holidays_path)

    if today in holidays:
        return []

    candidates = []
    for member in members:
        contact = contacts.get(member.member_id)

        if not is_eligible(member, contact, today):
            continue

        score = calculate_score(member, contact, today)
        window = "morning" if member.age >= 80 else "afternoon"

        candidates.append(CheckInCandidate(
            member_id=member.member_id,
            full_name=member.full_name,
            priority_score=score,
            recommended_window=window,
        ))

    candidates.sort(key=lambda c: c.priority_score, reverse=True)

    return candidates[:top_n]
