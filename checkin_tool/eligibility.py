from datetime import date
from typing import Optional

from checkin_tool.models import ContactRecord, Member

MINIMUM_DAYS_BETWEEN_CONTACTS = 7


def is_eligible(member: Member, contact: Optional[ContactRecord], today: date) -> bool:
    if member.preferred_channel is None:
        return False

    if contact is None:
        return True

    return (today - contact.last_contact_date).days >= MINIMUM_DAYS_BETWEEN_CONTACTS
