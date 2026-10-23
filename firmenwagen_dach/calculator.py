# -*- coding: utf-8 -*-
"""
Berechnungskern für Firmenwagen, 1%-Methode, Fahrtenbuch und Sachbezug 2026.
"""
from typing import Optional, List
from .models import (
    PauschaleResult,
    FahrtenbuchResult,
    ComparisonResult,
    BreakEvenResult,
)
from .rates import (
    COUNTRY_CONFIGS,
    GermanyRates,
    AustriaRates,
    SwitzerlandRates,
)
from .validator import (
    validate_country,
    validate_vehicle_type,
    validate_numeric,
)


def calculate_pauschale(
    country: str,
    gross_list_price: float,
    vehicle_type: str = "ice",
    distance_km: float = 0.0,
    co2_g_km: float = 130.0,
    is_half_sachbezug: bool = False,
    co_payment_monthly: float = 0.0,
    total_annual_costs: Optional[float] = None,
) -> PauschaleResult:
    """
    Berechnet den geldwerten Vorteil (Sachbezug) nach der Pauschalmethode 2026.
    """
    c = validate_country(country)
    vt = validate_vehicle_type(vehicle_type)
    price = validate_numeric(gross_list_price, "gross_list_price", min_val=0.0)
    dist = validate_numeric(distance_km, "distance_km", min_val=0.0)
    co2 = validate_numeric(co2_g_km, "co2_g_km", min_val=0.0)
    copay = validate_numeric(co_payment_monthly, "co_payment_monthly", min_val=0.0)

    cfg = COUNTRY_CONFIGS[c]
    currency = cfg.CURRENCY
    notes: List[str] = []

    rate_priv = 0.0
    rate_comm = 0.0
    priv_gwv = 0.0
    comm_gwv = 0.0

    if c == "DE":
        # Abrundung auf volle 100 Euro gem. § 6 Abs. 1 Nr. 4 EStG
        blp_rounded = float(int(price // 100) * 100)
        
        if vt == "bev":
            if blp_rounded <= GermanyRates.BEV_BLP_MAX_025:
                rate_priv = GermanyRates.RATE_BEV_UNDER_CAP
                rate_comm = GermanyRates.RATE_COMMUTE_BEV_UNDER
                notes.append(f"0,25 % Elektro-Regelung angewandt (BLP <= {GermanyRates.BEV_BLP_MAX_025:,.0f} € nach Wachstumschancengesetz).")
            else:
                rate_priv = GermanyRates.RATE_BEV_OVER_CAP
                rate_comm = GermanyRates.RATE_COMMUTE_BEV_OVER
                notes.append(f"0,5 % Elektro-Regelung angewandt (BLP übersteigt {GermanyRates.BEV_BLP_MAX_025:,.0f} €).")
        elif vt == "phev":
            rate_priv = GermanyRates.RATE_PHEV
            rate_comm = GermanyRates.RATE_COMMUTE_PHEV
            notes.append("0,5 % Plug-in-Hybrid Regelung angewandt.")
        else:
            rate_priv = GermanyRates.RATE_ICE
            rate_comm = GermanyRates.RATE_COMMUTE_ICE
            notes.append("1,0 % Standard-Pauschalregelung angewandt.")

        priv_gwv = blp_rounded * rate_priv
        comm_gwv = blp_rounded * rate_comm * dist

    elif c == "AT":
        # Österreich: Sachbezugswerteverordnung 2026
        if vt == "bev":
            rate_priv = AustriaRates.RATE_BEV
            priv_gwv = 0.0
            notes.append("0,0 % Sachbezug: Reine Elektrofahrzeuge sind in Österreich vollständig steuerbefreit (§ 4 Abs. 1 SBV).")
        else:
            is_low_co2 = (co2 <= AustriaRates.CO2_LIMIT_2026)
            if is_half_sachbezug:
                if is_low_co2:
                    rate_priv = AustriaRates.HALF_RATE_LOW_CO2
                    priv_gwv = min(price * rate_priv, AustriaRates.HALF_CAP_LOW_CO2)
                    notes.append("Halber Sachbezug (0,75 %, max. 360 €) bei niedriger CO2-Emission (<= 121 g/km).")
                else:
                    rate_priv = AustriaRates.HALF_RATE_STANDARD
                    priv_gwv = min(price * rate_priv, AustriaRates.HALF_CAP_STANDARD)
                    notes.append("Halber Sachbezug (1,0 %, max. 480 €) bei Standard-CO2-Emission (> 121 g/km).")
            else:
                if is_low_co2:
                    rate_priv = AustriaRates.RATE_LOW_CO2
                    priv_gwv = min(price * rate_priv, AustriaRates.CAP_LOW_CO2)
                    notes.append("1,5 % Sachbezug (max. 720 € mtl.) bei CO2 <= 121 g/km.")
                else:
                    rate_priv = AustriaRates.RATE_STANDARD
                    priv_gwv = min(price * rate_priv, AustriaRates.CAP_STANDARD)
                    notes.append("2,0 % Sachbezug (max. 960 € mtl.) bei CO2 > 121 g/km.")

        comm_gwv = 0.0  # Im österreichischen Sachbezug bereits abgegolten
        rate_comm = 0.0

    elif c == "CH":
        # Schweiz: ESTV Lohnausweis Wegleitung (0,9% monatlich)
        rate_priv = SwitzerlandRates.RATE_MONTHLY
        priv_gwv = max(price * rate_priv, SwitzerlandRates.MIN_MONTHLY)
        comm_gwv = 0.0  # Arbeitsweg ist in den 0,9 % bereits integriert
        rate_comm = 0.0
        notes.append("0,9 % ESTV Monatspauschale (inklusive Arbeitsweg gem. Wegleitung zum Lohnausweis).")

    raw_monthly = priv_gwv + comm_gwv
    net_monthly = max(0.0, raw_monthly - copay)
    annual_raw = net_monthly * 12.0

    cost_cap_applied = False
    cost_cap_amount: Optional[float] = None

    # BMF-Kostendeckelung (Deutschland): GWV darf die tatsächlichen Gesamtkosten p.a. nicht übersteigen
    if c == "DE" and total_annual_costs is not None and total_annual_costs >= 0:
        if annual_raw > total_annual_costs:
            cost_cap_applied = True
            cost_cap_amount = total_annual_costs
            annual_raw = total_annual_costs
            net_monthly = total_annual_costs / 12.0
            notes.append(f"BMF-Kostendeckelung greift: Geldwerter Vorteil auf tatsächliche Gesamtkosten ({total_annual_costs:,.2f} €) begrenzt.")

    return PauschaleResult(
        country=c,
        currency=currency,
        gross_list_price=price,
        effective_rate_private=rate_priv,
        effective_rate_commute=rate_comm,
        private_gwv_monthly=round(priv_gwv, 2),
        commute_gwv_monthly=round(comm_gwv, 2),
        total_gwv_monthly_raw=round(raw_monthly, 2),
        co_payment_monthly=round(copay, 2),
        total_gwv_monthly=round(net_monthly, 2),
        total_gwv_annual=round(annual_raw, 2),
        cost_cap_applied=cost_cap_applied,
        cost_cap_amount=cost_cap_amount,
        notes=notes,
    )


def calculate_fahrtenbuch(
    total_annual_costs: float,
    total_annual_km: float,
    private_km_annual: float,
    commute_km_annual: float = 0.0,
    co_payment_annual: float = 0.0,
    country: str = "DE",
) -> FahrtenbuchResult:
    """
    Berechnet den geldwerten Vorteil nach der Fahrtenbuchmethode.
    """
    c = validate_country(country)
    costs = validate_numeric(total_annual_costs, "total_annual_costs", min_val=0.0)
    km_tot = validate_numeric(total_annual_km, "total_annual_km", min_val=0.0)
    km_priv = validate_numeric(private_km_annual, "private_km_annual", min_val=0.0)
    km_comm = validate_numeric(commute_km_annual, "commute_km_annual", min_val=0.0)
    copay = validate_numeric(co_payment_annual, "co_payment_annual", min_val=0.0)

    cfg = COUNTRY_CONFIGS[c]
    currency = cfg.CURRENCY

    if km_tot <= 0.0:
        cost_per_km = 0.0
        km_biz = 0.0
        pct_priv = 0.0
        pct_comm = 0.0
    else:
        cost_per_km = costs / km_tot
        km_biz = max(0.0, km_tot - km_priv - km_comm)
        pct_priv = round((km_priv / km_tot) * 100.0, 2)
        pct_comm = round((km_comm / km_tot) * 100.0, 2)

    priv_gwv = km_priv * cost_per_km
    # In DE muss auch der Arbeitsweg mit den tatsächlichen km-Kosten angesetzt werden (§ 8 Abs. 2 S. 4 EStG)
    comm_gwv = km_comm * cost_per_km if c == "DE" else 0.0

    raw_annual = priv_gwv + comm_gwv
    net_annual = max(0.0, raw_annual - copay)
    net_monthly = net_annual / 12.0

    return FahrtenbuchResult(
        currency=currency,
        total_annual_costs=round(costs, 2),
        total_annual_km=round(km_tot, 1),
        cost_per_km=round(cost_per_km, 4),
        private_km_annual=round(km_priv, 1),
        commute_km_annual=round(km_comm, 1),
        business_km_annual=round(km_biz, 1),
        private_share_percent=pct_priv,
        commute_share_percent=pct_comm,
        private_gwv_annual=round(priv_gwv, 2),
        commute_gwv_annual=round(comm_gwv, 2),
        total_gwv_annual_raw=round(raw_annual, 2),
        co_payment_annual=round(copay, 2),
        total_gwv_annual=round(net_annual, 2),
        total_gwv_monthly=round(net_monthly, 2),
    )


def compare_methods(
    country: str,
    gross_list_price: float,
    vehicle_type: str = "ice",
    distance_km: float = 0.0,
    co2_g_km: float = 130.0,
    is_half_sachbezug: bool = False,
    total_annual_costs: float = 12000.0,
    total_annual_km: float = 30000.0,
    private_km_annual: float = 6000.0,
    commute_days_annual: int = 220,
    tax_rate: float = 0.40,
    co_payment_monthly: float = 0.0,
) -> ComparisonResult:
    """
    Vergleicht 1%-Pauschalmethode und Fahrtenbuch und ermittelt Steuerersparnis und Break-Even.
    """
    c = validate_country(country)
    tax_r = validate_numeric(tax_rate, "tax_rate", min_val=0.0)
    comm_km_annual = distance_km * 2.0 * commute_days_annual if c == "DE" else 0.0
    copay_annual = co_payment_monthly * 12.0

    res_pauschale = calculate_pauschale(
        country=c,
        gross_list_price=gross_list_price,
        vehicle_type=vehicle_type,
        distance_km=distance_km,
        co2_g_km=co2_g_km,
        is_half_sachbezug=is_half_sachbezug,
        co_payment_monthly=co_payment_monthly,
        total_annual_costs=total_annual_costs,
    )

    res_fb = calculate_fahrtenbuch(
        total_annual_costs=total_annual_costs,
        total_annual_km=total_annual_km,
        private_km_annual=private_km_annual,
        commute_km_annual=comm_km_annual,
        co_payment_annual=copay_annual,
        country=c,
    )

    pauschale_tax = res_pauschale.total_gwv_annual * tax_r
    fb_tax = res_fb.total_gwv_annual * tax_r
    savings_with_fb = pauschale_tax - fb_tax

    be = calculate_break_even(
        country=c,
        gross_list_price=gross_list_price,
        vehicle_type=vehicle_type,
        distance_km=distance_km,
        total_annual_costs=total_annual_costs,
        total_annual_km=total_annual_km,
    )

    if savings_with_fb >= 50.0:
        recommended = "FAHRTENBUCH"
        summary = (
            f"Fahrtenbuch empfohlen: Steuerersparnis von ca. {savings_with_fb:,.2f} {res_pauschale.currency} p.a. "
            f"gegenüber der Pauschalmethode. Break-Even liegt bei {be.break_even_private_km:,.0f} km Privatfahrt."
        )
    elif savings_with_fb <= -50.0:
        recommended = "PAUSCHALE"
        summary = (
            f"Pauschalmethode empfohlen: Spart ca. {abs(savings_with_fb):,.2f} {res_pauschale.currency} p.a. Steuerlast "
            f"gegenüber dem Fahrtenbuch und vermeidet lückenlosen Dokumentationsaufwand."
        )
    else:
        recommended = "GLEICHWERTIG"
        summary = "Beide Methoden führen zu einer annähernd identischen steuerlichen Belastung (+/- 50 € p.a.)."

    return ComparisonResult(
        country=c,
        currency=res_pauschale.currency,
        pauschale=res_pauschale,
        fahrtenbuch=res_fb,
        tax_rate=tax_r,
        pauschale_tax_annual=round(pauschale_tax, 2),
        fahrtenbuch_tax_annual=round(fb_tax, 2),
        tax_savings_with_fahrtenbuch=round(savings_with_fb, 2),
        recommended_method=recommended,
        break_even_private_km=be.break_even_private_km,
        summary=summary,
    )


def calculate_break_even(
    country: str,
    gross_list_price: float,
    vehicle_type: str = "ice",
    distance_km: float = 0.0,
    total_annual_costs: float = 12000.0,
    total_annual_km: float = 30000.0,
) -> BreakEvenResult:
    """
    Ermittelt die Break-Even Privatkilometer, ab denen das Fahrtenbuch teurer wird als die Pauschale.
    """
    c = validate_country(country)
    p_res = calculate_pauschale(
        country=c,
        gross_list_price=gross_list_price,
        vehicle_type=vehicle_type,
        distance_km=distance_km,
    )
    
    if total_annual_km <= 0 or total_annual_costs <= 0:
        return BreakEvenResult(
            country=c,
            currency=p_res.currency,
            break_even_private_km=0.0,
            break_even_private_percent=0.0,
            explanation="Unzureichende Fahrleistungs- oder Kostendaten für Break-Even-Ermittlung."
        )

    cost_per_km = total_annual_costs / total_annual_km
    # Pauschal-GWV p.a.
    pauschale_gwv = p_res.total_gwv_annual
    
    # Break-Even km = Pauschale-GWV / Kosten_pro_km
    be_km = pauschale_gwv / cost_per_km if cost_per_km > 0 else 0.0
    be_pct = (be_km / total_annual_km) * 100.0 if total_annual_km > 0 else 0.0

    exp = (
        f"Bis zu {be_km:,.0f} km Privatfahrt pro Jahr ({be_pct:.1f} % der Gesamtfahrleistung) "
        f"ist das Fahrtenbuch steuerlich günstiger als die Pauschale."
    )

    return BreakEvenResult(
        country=c,
        currency=p_res.currency,
        break_even_private_km=round(be_km, 1),
        break_even_private_percent=round(be_pct, 1),
        explanation=exp,
    )
