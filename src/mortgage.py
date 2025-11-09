"""
FINE3300 – Assignment 2 (Part A)
Author: Abdallah Al Ghoul
Date: 2025-11-08

Extends the Assignment 1 mortgage class:
- Computes payments for six frequencies (monthly, semi-monthly, bi-weekly, weekly, rapid bi-weekly, rapid weekly)
- Exports six amortization schedules (Pandas → Excel, 6 sheets)
- Plots balance decline for all six on one Matplotlib figure
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, List
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


@dataclass(frozen=True)
class MortgageParams:
    principal: float
    quoted_rate_percent: float   # annual nominal %, semi-annual compounding
    amort_years: int
    term_years: int

    def validate(self) -> None:
        if self.principal <= 0:
            raise ValueError("Principal must be positive.")
        if self.quoted_rate_percent < 0:
            raise ValueError("Quoted rate percent must be non-negative.")
        if self.amort_years <= 0:
            raise ValueError("Amortization years must be positive.")
        if self.term_years <= 0:
            raise ValueError("Term years must be positive.")
        if self.term_years > self.amort_years:
            raise ValueError("Term years cannot exceed amortization years.")


class MortgageCalculator:
    @staticmethod
    def ear_from_semi_annual_quote(quoted_rate_percent: float) -> float:
        j = quoted_rate_percent / 100.0
        return (1 + j / 2) ** 2 - 1

    @staticmethod
    def pva(rate: float, n: int) -> float:
        if rate == 0:
            return n
        return (1 - (1 + rate) ** (-n)) / rate

    @staticmethod
    def periodic_rate(ear: float, m: int) -> float:
        return (1 + ear) ** (1 / m) - 1

    @classmethod
    def level_payment(cls, principal: float, quoted_rate_percent: float, amort_years: int, m: int) -> float:
        ear = cls.ear_from_semi_annual_quote(quoted_rate_percent)
        r = cls.periodic_rate(ear, m)
        n = int(amort_years * m)
        return principal / cls.pva(r, n)


class MortgageSchedule:
    FREQS: Dict[str, Tuple[int, str]] = {
        "monthly":        (12, "Monthly"),
        "semi_monthly":   (24, "Semi-monthly"),
        "bi_weekly":      (26, "Bi-weekly"),
        "weekly":         (52, "Weekly"),
        "rapid_biweekly": (26, "Rapid Bi-weekly"),
        "rapid_weekly":   (52, "Rapid Weekly"),
    }

    def __init__(self, params: MortgageParams) -> None:
        params.validate()
        self.params = params
        self._ear = MortgageCalculator.ear_from_semi_annual_quote(params.quoted_rate_percent)
        self._standard_monthly_pmt = MortgageCalculator.level_payment(
            principal=params.principal,
            quoted_rate_percent=params.quoted_rate_percent,
            amort_years=params.amort_years,
            m=12,
        )

    def payment_amounts(self) -> Dict[str, float]:
        p = self.params
        payments = {}
        for key, (m, _) in self.FREQS.items():
            if key.startswith("rapid"):
                continue
            payments[key] = MortgageCalculator.level_payment(p.principal, p.quoted_rate_percent, p.amort_years, m)
        payments["rapid_biweekly"] = self._standard_monthly_pmt / 2.0
        payments["rapid_weekly"] = self._standard_monthly_pmt / 4.0
        return {k: float(np.round(v, 2)) for k, v in payments.items()}

    def build_schedule_df(self, freq_key: str) -> pd.DataFrame:
        if freq_key not in self.FREQS:
            raise KeyError(f"Unknown frequency: {freq_key}")
        p = self.params
        m, label = self.FREQS[freq_key]
        r = MortgageCalculator.periodic_rate(self._ear, m)
        if freq_key in ("rapid_biweekly", "rapid_weekly"):
            payment = self._standard_monthly_pmt / (2 if freq_key == "rapid_biweekly" else 4)
        else:
            payment = MortgageCalculator.level_payment(p.principal, p.quoted_rate_percent, p.amort_years, m)
        n_term = int(p.term_years * m)
        balance = float(p.principal)
        rows: List[Tuple[int, float, float, float, float]] = []
        for t in range(1, n_term + 1):
            start = balance
            interest = start * r
            principal_repay = payment - interest
            if principal_repay > start:
                payment_eff = start + interest
                end = 0.0
                rows.append((t, start, interest, payment_eff, end))
                balance = end
                break
            else:
                end = start - principal_repay
                rows.append((t, start, interest, payment, end))
                balance = end
            if balance <= 0.01:
                break
        df = pd.DataFrame(rows, columns=["Period", "StartBalance", "Interest", "Payment", "EndBalance"])
        df.attrs["FrequencyLabel"] = label
        df.attrs["PaymentsPerYear"] = m
        return df

    def all_schedules_to_excel(self, path: str) -> None:
        with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
            for key in self.FREQS:
                df = self.build_schedule_df(key)
                df.to_excel(writer, index=False, sheet_name=self.FREQS[key][1])

    def plot_balances(self, path: str) -> None:
        plt.figure(figsize=(9, 5))
        for key in self.FREQS:
            df = self.build_schedule_df(key)
            plt.plot(df["Period"], df["EndBalance"], label=self.FREQS[key][1])
        plt.title("Loan Balance Decline by Payment Frequency")
        plt.xlabel("Period")
        plt.ylabel("Ending Balance ($)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(path, dpi=200)
        plt.close()


__all__ = ["MortgageParams", "MortgageCalculator", "MortgageSchedule"]
