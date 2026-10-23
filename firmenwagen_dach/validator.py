# -*- coding: utf-8 -*-
"""
Eingabevalidierung für Firmenwagen-Rechner.
"""
from typing import Tuple


def validate_country(country: str) -> str:
    c = (country or "DE").strip().upper()
    if c not in ("DE", "AT", "CH"):
        raise ValueError(f"Ungültiger Ländercode '{country}'. Erlaubt sind DE, AT, CH.")
    return c


def validate_vehicle_type(vehicle_type: str) -> str:
    v = (vehicle_type or "ice").strip().lower()
    if v not in ("ice", "phev", "bev"):
        raise ValueError(f"Ungültiger Antriebstyp '{vehicle_type}'. Erlaubt sind ice, phev, bev.")
    return v


def validate_numeric(val: float, name: str, min_val: float = 0.0) -> float:
    try:
        f = float(val)
    except (TypeError, ValueError):
        raise ValueError(f"Parameter '{name}' muss eine Zahl sein.")
    if f < min_val:
        raise ValueError(f"Parameter '{name}' darf nicht kleiner als {min_val} sein.")
    return f
