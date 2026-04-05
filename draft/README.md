# Clique Check-In Tool

A CLI tool that helps community coordinators identify which members need a check-in today.

---

## How to Run

### Install
```bash
pip install -e .
```

### Run the tool
```bash
checkin --top 5
```

### Available arguments
| Argument | Required | Default | Description |
|---|---|---|---|
| `--members` | No | `data/members.csv` | Path to members CSV file |
| `--contacts` | No | `data/last_contacts.csv` | Path to last contacts CSV file |
| `--holidays` | No | `data/holidays.json` | Path to holidays JSON file |
| `--top` | No | 10 | Number of candidates to return (min 1) |
| `--date` | No | today | Override today's date for testing (YYYY-MM-DD) |

### Run tests
```bash
pip install -e ".[dev]"
pytest -v
```

---

## Assumptions

- **Date format:** All dates in CSV and JSON files follow `YYYY-MM-DD`.
- **`risk_flags` column:** A semicolon-separated string (e.g. `"lives_alone;recent_discharge"`). Empty means no flags.
- **Duplicate contact records:** If a member appears more than once in `last_contacts.csv`, the record with the most recent `last_contact_date` is used, regardless of row order.
- **`days_since_last_contact` for uncontacted members:** Members with no contact record are eligible (never contacted), and their days component in the score defaults to `0`.
- **Holiday check:** If today is a holiday, no check-ins are scheduled for anyone — the tool exits early with a message.
- **`preferred_channel`:** An empty or blank value is treated as no valid channel, making the member ineligible.

---

## What I Would Improve With More Time

- **Output formats:** Add `--output json` or `--output csv` flags for programmatic consumption.
- **Configurable scoring weights:** Move the scoring constants (`+3`, `+2`, etc.) to a config file so they can be adjusted without touching code.
- **Stricter input validation:** Validate CSV column headers on load and raise a clear error if required columns are missing.
- **Logging:** Replace `print` warnings with Python's `logging` module for better control over verbosity levels.
