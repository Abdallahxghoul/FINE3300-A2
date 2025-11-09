"""
CLI runner for FINE3300 – Assignment 2 (Part A)
Example run:
python -m src.part_a_run --principal 500000 --rate 5.49 --amort 25 --term 5 --excel out/part_a_loan_schedules.xlsx --png out/part_a_balances.png
"""
import argparse
from pathlib import Path
from .mortgage import MortgageParams, MortgageSchedule


def parse_args():
    ap = argparse.ArgumentParser(description="Generate loan payment schedules and balance plot.")
    ap.add_argument("--principal", type=float, required=True)
    ap.add_argument("--rate", type=float, required=True)
    ap.add_argument("--amort", type=int, required=True)
    ap.add_argument("--term", type=int, required=True)
    ap.add_argument("--excel", type=str, required=True)
    ap.add_argument("--png", type=str, required=True)
    return ap.parse_args()


def main():
    args = parse_args()
    params = MortgageParams(
        principal=args.principal,
        quoted_rate_percent=args.rate,
        amort_years=args.amort,
        term_years=args.term,
    )
    sched = MortgageSchedule(params)
    Path(args.excel).parent.mkdir(parents=True, exist_ok=True)
    sched.all_schedules_to_excel(args.excel)
    Path(args.png).parent.mkdir(parents=True, exist_ok=True)
    sched.plot_balances(args.png)
    for k, v in sched.payment_amounts().items():
        print(f"{k:>15s}: ${v:,.2f}")


if __name__ == "__main__":
    main()
