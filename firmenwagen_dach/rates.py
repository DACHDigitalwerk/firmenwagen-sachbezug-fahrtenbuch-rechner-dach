# -*- coding: utf-8 -*-
"""
Amtliche Steuersätze, Schwellenwerte und Sachbezugsregelungen 2026 für DE, AT, CH.
"""
from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class GermanyRates:
    COUNTRY = "DE"
    CURRENCY = "EUR"
    LEGAL_BASIS = "§ 6 Abs. 1 Nr. 4 EStG / Wachstumschancengesetz 2026"
    
    # Bruttolistenpreis (BLP) Grenzen
    BEV_BLP_MAX_025 = 70000.0  # Anhebung von 60k auf 70k durch Wachstumschancengesetz
    
    # Monatliche Pauschalsätze Privatnutzung
    RATE_ICE = 0.01          # 1,0 % für Verbrenner & reguläre Hybride
    RATE_PHEV = 0.005        # 0,5 % für qualifizierte Plug-in-Hybride (mind. 80km oder max 50g CO2)
    RATE_BEV_UNDER_CAP = 0.0025  # 0,25 % für Elektroautos bis 70.000 € BLP
    RATE_BEV_OVER_CAP = 0.005   # 0,5 % für Elektroautos über 70.000 € BLP
    
    # Monatliche Pauschalsätze Arbeitsweg (pro Entfernungskilometer)
    RATE_COMMUTE_ICE = 0.0003       # 0,03 % pro km
    RATE_COMMUTE_PHEV = 0.00015     # 0,015 % pro km
    RATE_COMMUTE_BEV_UNDER = 0.000075  # 0,0075 % pro km
    RATE_COMMUTE_BEV_OVER = 0.00015    # 0,015 % pro km


@dataclass(frozen=True)
class AustriaRates:
    COUNTRY = "AT"
    CURRENCY = "EUR"
    LEGAL_BASIS = "§ 4 Sachbezugswerteverordnung (BMF 2026)"
    
    # CO2-Grenzwerte nach WLTP für Erstzulassungen 2026
    CO2_LIMIT_2026 = 121.0  # g/km
    
    # Monatliche Sachbezugssätze
    RATE_BEV = 0.00         # 0,0 % für reine Elektrofahrzeuge (vollständig befreit)
    RATE_LOW_CO2 = 0.015    # 1,5 % für emissionsarme Fahrzeuge (<= 121 g/km)
    CAP_LOW_CO2 = 720.0     # Maximal 720 € monatlich
    
    RATE_STANDARD = 0.020   # 2,0 % für Standard-Fahrzeuge (> 121 g/km)
    CAP_STANDARD = 960.0    # Maximal 960 € monatlich
    
    # Halber Sachbezug bei unter 500 km Privatfahrt/Monat (6.000 km/Jahr)
    HALF_RATE_LOW_CO2 = 0.0075
    HALF_CAP_LOW_CO2 = 360.0
    HALF_RATE_STANDARD = 0.010
    HALF_CAP_STANDARD = 480.0
    
    # Arbeitsweg ist im österreichischen Sachbezug bereits integriert


@dataclass(frozen=True)
class SwitzerlandRates:
    COUNTRY = "CH"
    CURRENCY = "CHF"
    LEGAL_BASIS = "ESTV Praxisfestlegung Wegleitung zum Lohnausweis (0,9% p.M.)"
    
    RATE_MONTHLY = 0.009    # 0,9 % monatlich auf Kaufpreis exkl. MwSt (10,8 % p.a.)
    MIN_MONTHLY = 150.0     # Mindestens 150 CHF monatlich
    
    # Arbeitsweg ist in der 0,9 % Pauschale voll abgegolten (Feld F im Lohnausweis)


COUNTRY_CONFIGS: Dict[str, Any] = {
    "DE": GermanyRates,
    "AT": AustriaRates,
    "CH": SwitzerlandRates,
}
