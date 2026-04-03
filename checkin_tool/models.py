from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Member:
    member_id: str
    full_name: str
    age: int
    preferred_channel: Optional[str]  # None means no valid channel
    recent_discharge: bool
    lives_alone: bool


@dataclass
class ContactRecord:
    member_id: str
    last_contact_date: date
    outcome: str  # e.g. "answered", "no_answer", "ok", "escalate"


@dataclass(frozen=True)
class CheckInCandidate:
    member_id: str
    full_name: str
    priority_score: float
    recommended_window: str  # "morning" or "afternoon"
