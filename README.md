# FINE3300 – Assignment 2 (Part A)
Computes six mortgage payment schedules and exports to Excel (6 sheets) + a balance decline plot.

## Run
```bash
python -m src.part_a_run \
  --principal 500000 --rate 5.49 --amort 25 --term 5 \
  --excel out/part_a_loan_schedules.xlsx \
  --png out/part_a_balances.png
