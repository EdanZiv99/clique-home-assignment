from datetime import date

import pytest

from checkin_tool.eligibility import is_eligible
from checkin_tool.models import ContactRecord, Member

TODAY = date(2026, 4, 5)


def make_member(**kwargs) -> Member:
    defaults = dict(
        member_id="1",
        full_name="Test Member",
        age=70,
        preferred_channel="call",
        recent_discharge=False,
        lives_alone=False,
    )
    return Member(**{**defaults, **kwargs})


def make_contact(days_ago: int, outcome: str = "answered") -> ContactRecord:
    return ContactRecord(
        member_id="1",
        last_contact_date=date.fromordinal(TODAY.toordinal() - days_ago),
        outcome=outcome,
    )


# --- Channel checks ---

def test_no_channel_is_not_eligible():
    member = make_member(preferred_channel=None)
    assert is_eligible(member, None, TODAY) is False


def test_valid_channel_with_no_contact_is_eligible():
    member = make_member(preferred_channel="call")
    assert is_eligible(member, None, TODAY) is True


# --- Days since last contact ---

def test_contacted_6_days_ago_is_not_eligible():
    member = make_member()
    contact = make_contact(days_ago=6)
    assert is_eligible(member, contact, TODAY) is False


def test_contacted_exactly_7_days_ago_is_eligible():
    member = make_member()
    contact = make_contact(days_ago=7)
    assert is_eligible(member, contact, TODAY) is True


def test_contacted_more_than_7_days_ago_is_eligible():
    member = make_member()
    contact = make_contact(days_ago=20)
    assert is_eligible(member, contact, TODAY) is True


# --- No contact record ---

def test_no_contact_record_is_eligible():
    member = make_member()
    assert is_eligible(member, None, TODAY) is True


# --- Combined: no channel + no contact ---

def test_no_channel_no_contact_is_not_eligible():
    member = make_member(preferred_channel=None)
    assert is_eligible(member, None, TODAY) is False


# --- Outcome does not affect eligibility ---

def test_no_answer_outcome_still_eligible_after_7_days():
    member = make_member()
    contact = make_contact(days_ago=10, outcome="no_answer")
    assert is_eligible(member, contact, TODAY) is True


def test_no_answer_outcome_not_eligible_within_7_days():
    member = make_member()
    contact = make_contact(days_ago=3, outcome="no_answer")
    assert is_eligible(member, contact, TODAY) is False
