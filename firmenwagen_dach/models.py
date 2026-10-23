# -*- coding: utf-8 -*-
"""
Datenmodelle für Firmenwagen-Besteuerung und Methodenvergleich.
"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class PauschaleResult:
    country: str
    currency: str
    gross_list_price: float
    effective_rate_private: float
    effective_rate_commute: float
    private_gwv_monthly: float
    commute_gwv_monthly: float
    total_gwv_monthly_raw: float
    co_payment_monthly: float
    total_gwv_monthly: float
    total_gwv_annual: float
    cost_cap_applied: bool
    cost_cap_amount: Optional[float] = None
    notes: Optional[List[str]] = None


@dataclass
class FahrtenbuchResult:
    currency: str
    total_annual_costs: float
    total_annual_km: float
    cost_per_km: float
    private_km_annual: float
    commute_km_annual: float
    business_km_annual: float
    private_share_percent: float
    commute_share_percent: float
    private_gwv_annual: float
    commute_gwv_annual: float
    total_gwv_annual_raw: float
    co_payment_annual: float
    total_gwv_annual: float
    total_gwv_monthly: float


@dataclass
class ComparisonResult:
    country: str
    currency: str
    pauschale: PauschaleResult
    fahrtenbuch: FahrtenbuchResult
    tax_rate: float
    pauschale_tax_annual: float
    fahrtenbuch_tax_annual: float
    tax_savings_with_fahrtenbuch: float
    recommended_method: str
    break_even_private_km: float
    summary: str


@dataclass
class BreakEvenResult:
    country: str
    currency: str
    break_even_private_km: float
    break_even_private_percent: float
    explanation: str
