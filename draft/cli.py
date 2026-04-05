import argparse
import sys
from datetime import date, datetime

from checkin_tool.loader import load_holidays
from checkin_tool.recommender import get_candidates


def positive_int(value: str) -> int:
    n = int(value)
    if n < 1:
        raise argparse.ArgumentTypeError("--top must be at least 1.")
    return n


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Identify members who need a check-in today.")
    parser.add_argument("--members", default="data/members.csv", help="Path to members.csv")
    parser.add_argument("--contacts", default="data/last_contacts.csv", help="Path to last_contacts.csv")
    parser.add_argument("--holidays", default="data/holidays.json", help="Path to holidays.json")
    parser.add_argument("--top", type=positive_int, default=10, help="Number of candidates to return (min 1)")
    parser.add_argument("--date", default=None, help="Override today's date (YYYY-MM-DD)")
    return parser.parse_args()


def print_results(candidates) -> None:
    header = f"{'#':<4} {'ID':<6} {'Name':<25} {'Score':<8} {'Window'}"
    print(header)
    print("-" * len(header))
    for i, c in enumerate(candidates, start=1):
        print(f"{i:<4} {c.member_id:<6} {c.full_name:<25} {c.priority_score:<8.2f} {c.recommended_window}")


def main() -> None:
    args = parse_args()

    try:
        today = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()

        holidays = load_holidays(args.holidays)
        if today in holidays:
            print("No check-ins scheduled — today is a holiday.")
            sys.exit(0)

        candidates = get_candidates(
            members_path=args.members,
            contacts_path=args.contacts,
            holidays_path=args.holidays,
            top_n=args.top,
            today=today,
        )

        if not candidates:
            print("No eligible members found for today.")
            sys.exit(0)

        print_results(candidates)

    except FileNotFoundError as e:
        print(f"[ERROR] File not found: {e.filename}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"[ERROR] Invalid value: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
