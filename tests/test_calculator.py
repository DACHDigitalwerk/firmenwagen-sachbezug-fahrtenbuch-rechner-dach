# -*- coding: utf-8 -*-
import pytest
from firmenwagen_dach.calculator import (
    calculate_pauschale,
    calculate_fahrtenbuch,
    compare_methods,
    calculate_break_even,
)
from firmenwagen_dach.validator import (
    validate_country,
    validate_vehicle_type,
    validate_numeric,
)


def test_de_ice_1_percent():
    # 50.000 € BLP, 20 km Entfernung
    res = calculate_pauschale(country="DE", gross_list_price=50000.0, vehicle_type="ice", distance_km=20.0)
    assert res.country == "DE"
    assert res.currency == "EUR"
    assert res.effective_rate_private == 0.01
    assert res.effective_rate_commute == 0.0003
    assert res.private_gwv_monthly == 500.0  # 1% von 50k
    assert res.commute_gwv_monthly == 300.0  # 0.03% * 50k * 20km = 15€ * 20 = 300€
    assert res.total_gwv_monthly == 800.0
    assert res.total_gwv_annual == 9600.0


def test_de_phev_05_percent():
    # 60.000 € BLP, 15 km Entfernung
    res = calculate_pauschale(country="DE", gross_list_price=60000.0, vehicle_type="phev", distance_km=15.0)
    assert res.effective_rate_private == 0.005
    assert res.effective_rate_commute == 0.00015
    assert res.private_gwv_monthly == 300.0  # 0.5% von 60k
    assert res.commute_gwv_monthly == 135.0  # 0.015% * 60k * 15km = 135€
    assert res.total_gwv_monthly == 435.0


def test_de_bev_under_70k_cap():
    # 68.500 € BLP (unter 70k € Grenze nach Wachstumschancengesetz) -> 0.25%
    res = calculate_pauschale(country="DE", gross_list_price=68500.0, vehicle_type="bev", distance_km=25.0)
    assert res.effective_rate_private == 0.0025
    assert res.effective_rate_commute == 0.000075
    # BLP 68.500 € -> 0.25% = 171.25 €
    assert res.private_gwv_monthly == 171.25
    # Commute: 68.500 * 0.000075 * 25 = 128.44 €
    assert res.commute_gwv_monthly == 128.44
    assert res.total_gwv_monthly == 299.69


def test_de_bev_over_70k_cap():
    # 85.000 € BLP (über 70k € Grenze) -> fällt auf 0.5% zurück
    res = calculate_pauschale(country="DE", gross_list_price=85000.0, vehicle_type="bev", distance_km=20.0)
    assert res.effective_rate_private == 0.005
    assert res.effective_rate_commute == 0.00015
    assert res.private_gwv_monthly == 425.0  # 0.5% von 85k
    assert res.commute_gwv_monthly == 255.0  # 0.015% * 85k * 20 = 255€


def test_de_cost_cap_kostendeckelung():
    # Wenn Pauschale höher als tatsächliche Kosten, greift Kostendeckelung
    # BLP 60.000 € ICE + 30 km = 600€ + 540€ = 1140€/mtl = 13.680 € p.a.
    # Tatsächliche Kosten nur 8.000 € p.a.
    res = calculate_pauschale(
        country="DE",
        gross_list_price=60000.0,
        vehicle_type="ice",
        distance_km=30.0,
        total_annual_costs=8000.0
    )
    assert res.cost_cap_applied is True
    assert res.total_gwv_annual == 8000.0
    assert pytest.approx(res.total_gwv_monthly, 0.01) == 8000.0 / 12.0


def test_de_co_payment_deduction():
    # 40.000 € ICE ohne Entfernung = 400 € GWV. Zuzahlung 150 € mtl. -> 250 € Netto-GWV
    res = calculate_pauschale(country="DE", gross_list_price=40000.0, co_payment_monthly=150.0)
    assert res.total_gwv_monthly_raw == 400.0
    assert res.co_payment_monthly == 150.0
    assert res.total_gwv_monthly == 250.0
    assert res.total_gwv_annual == 3000.0


def test_at_bev_zero_sachbezug():
    # Österreich: Elektrofahrzeuge = 0% Sachbezug
    res = calculate_pauschale(country="AT", gross_list_price=55000.0, vehicle_type="bev")
    assert res.country == "AT"
    assert res.currency == "EUR"
    assert res.effective_rate_private == 0.0
    assert res.total_gwv_monthly == 0.0
    assert res.total_gwv_annual == 0.0


def test_at_low_co2_15_percent_and_cap():
    # Österreich: CO2 <= 121g/km -> 1.5%, max 720€
    # Anschaffung 40.000 € -> 1.5% = 600 € (< 720 €)
    res1 = calculate_pauschale(country="AT", gross_list_price=40000.0, vehicle_type="ice", co2_g_km=110.0)
    assert res1.effective_rate_private == 0.015
    assert res1.total_gwv_monthly == 600.0

    # Anschaffung 60.000 € -> 1.5% = 900 € -> gedeckelt auf 720 €
    res2 = calculate_pauschale(country="AT", gross_list_price=60000.0, vehicle_type="ice", co2_g_km=110.0)
    assert res2.total_gwv_monthly == 720.0


def test_at_standard_co2_20_percent_and_cap():
    # Österreich: CO2 > 121g/km -> 2.0%, max 960€
    # Anschaffung 35.000 € -> 2.0% = 700 €
    res1 = calculate_pauschale(country="AT", gross_list_price=35000.0, vehicle_type="ice", co2_g_km=145.0)
    assert res1.effective_rate_private == 0.02
    assert res1.total_gwv_monthly == 700.0

    # Anschaffung 60.000 € -> 2.0% = 1200 € -> gedeckelt auf 960 €
    res2 = calculate_pauschale(country="AT", gross_list_price=60000.0, vehicle_type="ice", co2_g_km=145.0)
    assert res2.total_gwv_monthly == 960.0


def test_at_half_sachbezug():
    # Halber Sachbezug bei unter 500 km Privatfahrt/Monat
    # Low CO2: 0.75% max 360€
    res_low = calculate_pauschale(country="AT", gross_list_price=40000.0, co2_g_km=100.0, is_half_sachbezug=True)
    assert res_low.total_gwv_monthly == 300.0  # 40k * 0.75%

    res_low_capped = calculate_pauschale(country="AT", gross_list_price=60000.0, co2_g_km=100.0, is_half_sachbezug=True)
    assert res_low_capped.total_gwv_monthly == 360.0  # Cap 360€

    # Standard CO2: 1.0% max 480€
    res_std = calculate_pauschale(country="AT", gross_list_price=40000.0, co2_g_km=140.0, is_half_sachbezug=True)
    assert res_std.total_gwv_monthly == 400.0

    res_std_capped = calculate_pauschale(country="AT", gross_list_price=60000.0, co2_g_km=140.0, is_half_sachbezug=True)
    assert res_std_capped.total_gwv_monthly == 480.0  # Cap 480€


def test_ch_estv_09_percent():
    # Schweiz: 0.9% pro Monat auf Kaufpreis exkl. MwSt
    # Kaufpreis 50.000 CHF -> 50.000 * 0.009 = 450 CHF / Monat (5.400 CHF p.a.)
    res = calculate_pauschale(country="CH", gross_list_price=50000.0)
    assert res.country == "CH"
    assert res.currency == "CHF"
    assert res.effective_rate_private == 0.009
    assert res.total_gwv_monthly == 450.0
    assert res.total_gwv_annual == 5400.0


def test_ch_estv_minimum_cap():
    # Schweiz Mindestsachbezug 150 CHF/Monat
    res = calculate_pauschale(country="CH", gross_list_price=10000.0)
    assert res.total_gwv_monthly == 150.0  # 10k * 0.9% = 90 < 150 CHF Min


def test_fahrtenbuch_calculation():
    # Gesamtkosten 12.000 €, Gesamt-km 30.000 km, Privat-km 6.000 km
    # Kostensatz = 0.40 €/km
    # Privat GWV = 6.000 * 0.40 = 2.400 € p.a. (200 € / Monat)
    res = calculate_fahrtenbuch(
        total_annual_costs=12000.0,
        total_annual_km=30000.0,
        private_km_annual=6000.0,
        commute_km_annual=0.0,
        country="DE"
    )
    assert res.cost_per_km == 0.40
    assert res.private_gwv_annual == 2400.0
    assert res.total_gwv_annual == 2400.0
    assert res.total_gwv_monthly == 200.0
    assert res.private_share_percent == 20.0


def test_comparison_fahrtenbuch_recommended():
    # 60.000 € BLP ICE, 25 km Pendelstrecke -> Pauschale = 600€ + 450€ = 1050€/mtl = 12.600 € p.a.
    # Steuerlast bei 40% = 5.040 €
    # Fahrtenbuch: Gesamtkosten 10.000 €, 30.000 km, nur 3.000 km privat (10%)
    # GWV FB = 1.000 € -> Steuerlast 400 €
    # Ersparnis mit FB = 4.640 €
    comp = compare_methods(
        country="DE",
        gross_list_price=60000.0,
        vehicle_type="ice",
        distance_km=25.0,
        total_annual_costs=10000.0,
        total_annual_km=30000.0,
        private_km_annual=3000.0,
        tax_rate=0.40
    )
    assert comp.recommended_method == "FAHRTENBUCH"
    assert comp.tax_savings_with_fahrtenbuch > 0


def test_comparison_pauschale_recommended():
    # Günstiger Kleinwagen 20.000 € Elektro (0.25%) -> Pauschale = 50 €/Monat = 600 € p.a.
    # Steuerlast bei 40% = 240 €
    # Fahrtenbuch bei 15.000 km privat und 8.000 € Kosten -> GWV wesentlich höher
    comp = compare_methods(
        country="DE",
        gross_list_price=20000.0,
        vehicle_type="bev",
        distance_km=0.0,
        total_annual_costs=8000.0,
        total_annual_km=20000.0,
        private_km_annual=15000.0,
        tax_rate=0.40
    )
    assert comp.recommended_method == "PAUSCHALE"
    assert comp.tax_savings_with_fahrtenbuch < 0


def test_break_even_calculation():
    # 40.000 € BLP ICE ohne Pendeln -> Pauschale GWV = 4.800 € p.a.
    # Gesamtkosten 12.000 € auf 30.000 km -> 0.40 €/km
    # Break-Even km = 4.800 / 0.40 = 12.000 km (40 % der Gesamtkilometer)
    be = calculate_break_even(
        country="DE",
        gross_list_price=40000.0,
        vehicle_type="ice",
        distance_km=0.0,
        total_annual_costs=12000.0,
        total_annual_km=30000.0
    )
    assert be.break_even_private_km == 12000.0
    assert be.break_even_private_percent == 40.0


def test_break_even_zero_division_safety():
    be = calculate_break_even(country="DE", gross_list_price=40000.0, total_annual_costs=0.0, total_annual_km=0.0)
    assert be.break_even_private_km == 0.0


def test_validator_country_errors():
    with pytest.raises(ValueError, match="Ungültiger Ländercode"):
        validate_country("US")


def test_validator_vehicle_type_errors():
    with pytest.raises(ValueError, match="Ungültiger Antriebstyp"):
        validate_vehicle_type("diesel_super")


def test_validator_numeric_errors():
    with pytest.raises(ValueError, match="Parameter 'price' darf nicht kleiner als"):
        validate_numeric(-50.0, "price", min_val=0.0)

    with pytest.raises(ValueError, match="muss eine Zahl sein"):
        validate_numeric("abc", "price")
