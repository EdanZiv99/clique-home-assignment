import json
import textwrap
from datetime import date

import pytest

from checkin_tool.recommender import get_candidates


# --- Helpers ---

def write_members(tmp_path, rows: str) -> str:
    p = tmp_path / "members.csv"
    p.write_text("member_id,full_name,age,preferred_channel,risk_flags\n" + textwrap.dedent(rows))
    return str(p)


def write_contacts(tmp_path, rows: str) -> str:
    p = tmp_path / "contacts.csv"
    p.write_text("member_id,last_contact_date,outcome\n" + textwrap.dedent(rows))
    return str(p)


def write_holidays(tmp_path, dates: list) -> str:
    p = tmp_path / "holidays.json"
    p.write_text(json.dumps(dates))
    return str(p)


TODAY = date(2026, 4, 5)
HOLIDAY = "2026-04-05"
NO_HOLIDAYS = []


# --- Holiday ---

def test_holiday_returns_empty_list(tmp_path):
    m = write_members(tmp_path, "1,Ruth Cohen,82,call,lives_alone\n")
    c = write_contacts(tmp_path, "1,2026-03-20,answered\n")
    h = write_holidays(tmp_path, [HOLIDAY])
    result = get_candidates(m, c, h, top_n=10, today=TODAY)
    assert result == []


# --- No eligible members ---

def test_recently_contacted_member_excluded(tmp_path):
    m = write_members(tmp_path, "1,Ruth Cohen,82,call,lives_alone\n")
    c = write_contacts(tmp_path, "1,2026-04-03,answered\n")  # 2 days ago
    h = write_holidays(tmp_path, NO_HOLIDAYS)
    result = get_candidates(m, c, h, top_n=10, today=TODAY)
    assert result == []


def test_no_channel_member_excluded(tmp_path):
    m = write_members(tmp_path, "1,Esther Mizrahi,88,,lives_alone\n")
    c = write_contacts(tmp_path, "1,2026-03-20,answered\n")
    h = write_holidays(tmp_path, NO_HOLIDAYS)
    result = get_candidates(m, c, h, top_n=10, today=TODAY)
    assert result == []


# --- No contact record ---

def test_never_contacted_member_is_eligible(tmp_path):
    m = write_members(tmp_path, "1,Moshe Goldberg,91,call,lives_alone;recent_discharge\n")
    c = write_contacts(tmp_path, "")  # no records
    h = write_holidays(tmp_path, NO_HOLIDAYS)
    result = get_candidates(m, c, h, top_n=10, today=TODAY)
    assert len(result) == 1
    assert result[0].member_id == "1"


# --- top_n ---

def test_top_n_limits_results(tmp_path):
    m = write_members(tmp_path, (
        "1,Ruth Cohen,82,call,lives_alone\n"
        "2,Sarah Adler,90,whatsapp,recent_discharge\n"
        "3,Moshe Goldberg,91,call,lives_alone;recent_discharge\n"
    ))
    c = write_contacts(tmp_path, (
        "1,2026-03-20,answered\n"
        "2,2026-03-20,answered\n"
        "3,2026-03-20,answered\n"
    ))
    h = write_holidays(tmp_path, NO_HOLIDAYS)
    result = get_candidates(m, c, h, top_n=2, today=TODAY)
    assert len(result) == 2


def test_top_n_larger_than_candidates_returns_all(tmp_path):
    m = write_members(tmp_path, "1,Ruth Cohen,82,call,lives_alone\n")
    c = write_contacts(tmp_path, "1,2026-03-20,answered\n")
    h = write_holidays(tmp_path, NO_HOLIDAYS)
    result = get_candidates(m, c, h, top_n=100, today=TODAY)
    assert len(result) == 1


# --- Sorting ---

def test_results_sorted_by_score_descending(tmp_path):
    m = write_members(tmp_path, (
        "1,Danny Israel,68,call,\n"                          # low score
        "2,Moshe Goldberg,91,call,lives_alone;recent_discharge\n"  # high score
    ))
    c = write_contacts(tmp_path, (
        "1,2026-03-20,answered\n"
        "2,2026-03-20,answered\n"
    ))
    h = write_holidays(tmp_path, NO_HOLIDAYS)
    result = get_candidates(m, c, h, top_n=10, today=TODAY)
    assert result[0].member_id == "2"
    assert result[1].member_id == "1"


# --- recommended_window ---

def test_age_80_gets_morning_window(tmp_path):
    m = write_members(tmp_path, "1,Ruth Cohen,80,call,\n")
    c = write_contacts(tmp_path, "1,2026-03-20,answered\n")
    h = write_holidays(tmp_path, NO_HOLIDAYS)
    result = get_candidates(m, c, h, top_n=10, today=TODAY)
    assert result[0].recommended_window == "morning"


def test_age_79_gets_afternoon_window(tmp_path):
    m = write_members(tmp_path, "1,Danny Israel,79,call,\n")
    c = write_contacts(tmp_path, "1,2026-03-20,answered\n")
    h = write_holidays(tmp_path, NO_HOLIDAYS)
    result = get_candidates(m, c, h, top_n=10, today=TODAY)
    assert result[0].recommended_window == "afternoon"


# --- Output fields ---

def test_candidate_fields_are_correct(tmp_path):
    m = write_members(tmp_path, "1,Ruth Cohen,82,call,lives_alone\n")
    c = write_contacts(tmp_path, "1,2026-03-20,answered\n")
    h = write_holidays(tmp_path, NO_HOLIDAYS)
    result = get_candidates(m, c, h, top_n=10, today=TODAY)
    candidate = result[0]
    assert candidate.member_id == "1"
    assert candidate.full_name == "Ruth Cohen"
    assert isinstance(candidate.priority_score, float)
    assert candidate.recommended_window == "morning"
