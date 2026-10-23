# -*- coding: utf-8 -*-
"""
firmenwagen_dach: DACH Firmenwagen-, 1%-Regelung- & Fahrtenbuch-Vergleichsrechner 2026.
Berechnungsmodell für Deutschland (§ 6 EStG), Österreich (§ 4 SBV) und die Schweiz (ESTV 0,9%).
"""

__version__ = "1.0.0"
__author__ = "DACH Digitalwerk"

from .models import (
    PauschaleResult,
    FahrtenbuchResult,
    ComparisonResult,
    BreakEvenResult,
)
from .calculator import (
    calculate_pauschale,
    calculate_fahrtenbuch,
    compare_methods,
    calculate_break_even,
)
from .rates import (
    COUNTRY_CONFIGS,
    GermanyRates,
    AustriaRates,
    SwitzerlandRates,
)

__all__ = [
    "PauschaleResult",
    "FahrtenbuchResult",
    "ComparisonResult",
    "BreakEvenResult",
    "calculate_pauschale",
    "calculate_fahrtenbuch",
    "compare_methods",
    "calculate_break_even",
    "COUNTRY_CONFIGS",
    "GermanyRates",
    "AustriaRates",
    "SwitzerlandRates",
]
