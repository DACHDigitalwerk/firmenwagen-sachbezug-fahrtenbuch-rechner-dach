# -*- coding: utf-8 -*-
"""
CLI-Interface für den DACH Firmenwagen-, 1%-Regelung- & Fahrtenbuch-Rechner.
Kommando: dach-firmenwagen
"""
import argparse
import json
import sys
from typing import Dict, Any, Optional, List
from .calculator import compare_methods


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DACH Firmenwagen-, 1%-Regelung- & Fahrtenbuch-Vergleichsrechner 2026 (DE, AT, CH)"
    )
    parser.add_argument(
        "--country", "-c",
        choices=["DE", "AT", "CH"],
        default="DE",
        help="Ländermodus: DE (Deutschland), AT (Österreich), CH (Schweiz)"
    )
    parser.add_argument(
        "--price", "-p",
        type=float,
        required=True,
        help="Bruttolistenpreis (DE) / Anschaffungskosten (AT) / Kaufpreis exkl. MwSt (CH)"
    )
    parser.add_argument(
        "--type", "-t",
        choices=["ice", "phev", "bev"],
        default="ice",
        help="Antriebsart: ice (Verbrenner), phev (Plug-in-Hybrid), bev (Elektro)"
    )
    parser.add_argument(
        "--distance", "-d",
        type=float,
        default=0.0,
        help="Einfache Entfernung Wohnung - erste Tätigkeitsstätte in km (nur DE relevant)"
    )
    parser.add_argument(
        "--co2",
        type=float,
        default=130.0,
        help="CO2-Ausstoß in g/km nach WLTP (relevant für Österreich)"
    )
    parser.add_argument(
        "--half-sachbezug",
        action="store_true",
        help="Österreich: Halber Sachbezug bei unter 500 km Privatfahrt/Monat (< 6.000 km p.a.)"
    )
    parser.add_argument(
        "--costs",
        type=float,
        default=12000.0,
        help="Tatsächliche Gesamtkosten des Fahrzeugs pro Jahr (AfA, Sprit, Versicherung, etc.)"
    )
    parser.add_argument(
        "--total-km",
        type=float,
        default=30000.0,
        help="Gesamte Jahresfahrleistung in Kilometern"
    )
    parser.add_argument(
        "--private-km",
        type=float,
        default=6000.0,
        help="Reine Privatfahrten pro Jahr in Kilometern"
    )
    parser.add_argument(
        "--tax-rate",
        type=float,
        default=0.40,
        help="Persönlicher Grenzsteuersatz (z. B. 0.40 für 40 Prozent)"
    )
    parser.add_argument(
        "--copay",
        type=float,
        default=0.0,
        help="Monatliche Eigenbeteiligung / Zuzahlung des Arbeitnehmers"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Ergebnis als formatiertes JSON ausgeben"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Dateipfad für JSON-Export"
    )
    return parser


def run_cli(args_list: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(args_list)

    comp = compare_methods(
        country=args.country,
        gross_list_price=args.price,
        vehicle_type=args.type,
        distance_km=args.distance,
        co2_g_km=args.co2,
        is_half_sachbezug=args.half_sachbezug,
        total_annual_costs=args.costs,
        total_annual_km=args.total_km,
        private_km_annual=args.private_km,
        tax_rate=args.tax_rate,
        co_payment_monthly=args.copay,
    )

    data_dict: Dict[str, Any] = {
        "country": comp.country,
        "currency": comp.currency,
        "recommended_method": comp.recommended_method,
        "summary": comp.summary,
        "pauschale": {
            "gross_list_price": comp.pauschale.gross_list_price,
            "private_gwv_monthly": comp.pauschale.private_gwv_monthly,
            "commute_gwv_monthly": comp.pauschale.commute_gwv_monthly,
            "total_gwv_monthly": comp.pauschale.total_gwv_monthly,
            "total_gwv_annual": comp.pauschale.total_gwv_annual,
            "tax_annual": comp.pauschale_tax_annual,
            "cost_cap_applied": comp.pauschale.cost_cap_applied,
            "notes": comp.pauschale.notes,
        },
        "fahrtenbuch": {
            "total_annual_costs": comp.fahrtenbuch.total_annual_costs,
            "cost_per_km": comp.fahrtenbuch.cost_per_km,
            "total_gwv_annual": comp.fahrtenbuch.total_gwv_annual,
            "total_gwv_monthly": comp.fahrtenbuch.total_gwv_monthly,
            "tax_annual": comp.fahrtenbuch_tax_annual,
        },
        "tax_savings_with_fahrtenbuch": comp.tax_savings_with_fahrtenbuch,
        "break_even_private_km": comp.break_even_private_km,
    }

    if args.json or args.output:
        json_str = json.dumps(data_dict, indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_str)
            print(f"Ergebnis erfolgreich in {args.output} gespeichert.")
        if args.json:
            print(json_str)
    else:
        print("=" * 68)
        print(f"🚗 DACH FIRMENWAGEN-VERGLEICHSRECHNER 2026 ({comp.country})")
        print("=" * 68)
        print(f"Empfohlene Methode   : {comp.recommended_method}")
        print(f"Steuerersparnis (FB) : {comp.tax_savings_with_fahrtenbuch:+,.2f} {comp.currency} p.a.")
        print(f"Break-Even Privat-km : {comp.break_even_private_km:,.0f} km/Jahr")
        print("-" * 68)
        print("Pauschalmethode:")
        print(f"  Geldwerter Vorteil : {comp.pauschale.total_gwv_monthly:,.2f} {comp.currency}/Monat ({comp.pauschale.total_gwv_annual:,.2f} {comp.currency}/Jahr)")
        print(f"  Steuerlast (~{args.tax_rate*100:.0f}%)  : {comp.pauschale_tax_annual:,.2f} {comp.currency}/Jahr")
        print("Fahrtenbuchmethode:")
        print(f"  Kilometersatz      : {comp.fahrtenbuch.cost_per_km:.4f} {comp.currency}/km")
        print(f"  Geldwerter Vorteil : {comp.fahrtenbuch.total_gwv_monthly:,.2f} {comp.currency}/Monat ({comp.fahrtenbuch.total_gwv_annual:,.2f} {comp.currency}/Jahr)")
        print(f"  Steuerlast (~{args.tax_rate*100:.0f}%)  : {comp.fahrtenbuch_tax_annual:,.2f} {comp.currency}/Jahr")
        print("-" * 68)
        print(f"Zusammenfassung: {comp.summary}")
        print("=" * 68)

    return 0


def main() -> None:
    sys.exit(run_cli())


if __name__ == "__main__":
    main()
