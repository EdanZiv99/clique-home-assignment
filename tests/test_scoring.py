from datetime import date

import pytest

from checkin_tool.models import ContactRecord, Member
from checkin_tool.scoring import calculate_score

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


# --- Individual scoring rules ---

def test_recent_discharge_adds_3():
    member = make_member(recent_discharge=True)
    score = calculate_score(member, None, TODAY)
    assert score == 3.0


def test_lives_alone_adds_2():
    member = make_member(lives_alone=True)
    score = calculate_score(member, None, TODAY)
    assert score == 2.0


def test_age_80_adds_1():
    member = make_member(age=80)
    score = calculate_score(member, None, TODAY)
    assert score == 1.0


def test_age_79_does_not_add_1():
    member = make_member(age=79)
    score = calculate_score(member, None, TODAY)
    assert score == 0.0


def test_no_answer_outcome_adds_1():
    member = make_member()
    contact = make_contact(days_ago=7, outcome="no_answer")
    score = calculate_score(member, contact, TODAY)
    assert score == pytest.approx(1.0 + 7 / 7)


def test_answered_outcome_does_not_add_1():
    member = make_member()
    contact = make_contact(days_ago=7, outcome="answered")
    score = calculate_score(member, contact, TODAY)
    assert score == pytest.approx(7 / 7)


# --- Days component ---

def test_days_component_14_days():
    member = make_member()
    contact = make_contact(days_ago=14)
    score = calculate_score(member, contact, TODAY)
    assert score == pytest.approx(14 / 7)


def test_no_contact_record_zero_days_component():
    member = make_member()
    score = calculate_score(member, None, TODAY)
    assert score == 0.0


# --- Combined scoring ---

def test_all_flags_max_score():
    member = make_member(recent_discharge=True, lives_alone=True, age=80)
    contact = make_contact(days_ago=14, outcome="no_answer")
    score = calculate_score(member, contact, TODAY)
    # +3 + +2 + +1 + +1 + 14/7 = 9.0
    assert score == pytest.approx(9.0)


def test_no_flags_zero_base_score():
    member = make_member()
    contact = make_contact(days_ago=7, outcome="answered")
    score = calculate_score(member, contact, TODAY)
    assert score == pytest.approx(1.0)


def test_no_flags_no_contact_zero_score():
    member = make_member()
    score = calculate_score(member, None, TODAY)
    assert score == 0.0
