# 🚗 DACH Firmenwagen-, 1%-Regelung- & Fahrtenbuch-Vergleichsrechner 2026

[![Python Tests](https://github.com/DACHDigitalwerk/firmenwagen-sachbezug-fahrtenbuch-rechner-dach/actions/workflows/python-tests.yml/badge.svg)](https://github.com/DACHDigitalwerk/firmenwagen-sachbezug-fahrtenbuch-rechner-dach/actions)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Web-App Live](https://img.shields.io/badge/Web--App-Live%20auf%20Netlify-emerald.svg)](https://dach-digitalwerk.netlify.app/firmenwagen-1-prozent-fahrtenbuch-rechner/)

> **Offizielles Open-Source-Berechnungspaket des DACH Digitalwerks.**  
> Interaktiver Online-Rechner mit druckfertiger DIN-A4 Auswertung:  
> 🔗 **[https://dach-digitalwerk.netlify.app/firmenwagen-1-prozent-fahrtenbuch-rechner/](https://dach-digitalwerk.netlify.app/firmenwagen-1-prozent-fahrtenbuch-rechner/)**

---

## 📌 Übersicht & Rechtsgrundlagen 2026

Dieses Python-Paket und CLI-Tool implementiert die offiziellen Berechnungsgrundlagen zur steuerlichen Dienstwagenbesteuerung und Gegenüberstellung von Pauschalmethode und Fahrtenbuch im DACH-Raum:

### 🇩🇪 Deutschland (§ 6 Abs. 1 Nr. 4 EStG)
* **1,0 % Pauschalregelung:** Für Verbrennungsmotoren und Mild-Hybride (1 % des auf volle 100 € abgerundeten Bruttolistenpreises monatlich).
* **0,5 % Halbierung:** Für qualifizierte Plug-in-Hybride (mind. 80 km elektrische Reichweite oder max. 50 g CO2/km) sowie Elektroautos mit einem Bruttolistenpreis über 70.000 €.
* **0,25 % Viertelung (Wachstumschancengesetz 2026):** Für reine Elektrofahrzeuge (BEV) bis zu einem Bruttolistenpreis von **70.000 €** (angehoben von zuvor 60.000 €).
* **Fahrten zwischen Wohnung und erster Tätigkeitsstätte:** 0,03 % (Verbrenner), 0,015 % (0,5 %-Klasse) bzw. 0,0075 % (0,25 %-Klasse) des BLP pro Entfernungskilometer und Monat.
* **BMF-Kostendeckelung:** Der geldwerte Vorteil wird automatisch auf die tatsächlichen Gesamtkosten des Fahrzeugs p.a. begrenzt.
* **Zuzahlungen des Arbeitnehmers:** Minderung des geldwerten Vorteils Euro für Euro (§ 8 Abs. 2 S. 4 EStG).

### 🇦🇹 Österreich (§ 4 SachbezugswerteVO 2026)
* **0,0 % Sachbezug:** Reine Elektrofahrzeuge sind in Österreich vollständig befreit.
* **1,5 % Sachbezug (max. 720 € mtl.):** Bei CO2-Emissionen bis 121 g/km nach WLTP.
* **2,0 % Sachbezug (max. 960 € mtl.):** Standard-Sachbezug bei CO2-Emissionen über 121 g/km.
* **Halber Sachbezug:** Bei nachweislich unter 500 km Privatfahrt monatlich (max. 6.000 km p.a.) Halbierung auf **0,75 % (max. 360 €)** bzw. **1,0 % (max. 480 €)**.

### 🇨🇭 Schweiz (ESTV Lohnausweis Wegleitung)
* **0,9 % Monatspauschale (10,8 % p.a.):** Berechnet auf den Kaufpreis exkl. MwSt (mindestens 150 CHF/Monat).
* **Arbeitsweg inklusive:** Mit der Pauschale ist auch der Arbeitsweg zwischen Wohnort und Arbeitsstätte abgegolten (Feld F im Lohnausweis).

---

## 🚀 Installation

```bash
git clone https://github.com/DACHDigitalwerk/firmenwagen-sachbezug-fahrtenbuch-rechner-dach.git
cd firmenwagen-sachbezug-fahrtenbuch-rechner-dach
pip install -e .
```

---

## 💻 CLI-Nutzung (`dach-firmenwagen`)

### 1. Schnelle Vergleichsrechnung (Deutschland)
```bash
dach-firmenwagen --country DE --price 65000 --type bev --distance 20 --costs 9000 --total-km 28000 --private-km 4000
```

### 2. Österreichischer Firmenwagen mit 1,5 % Sachbezug
```bash
dach-firmenwagen --country AT --price 45000 --type ice --co2 115 --total-km 30000 --private-km 5000
```

### 3. Schweizer Geschäftsfahrzeug mit JSON-Export
```bash
dach-firmenwagen --country CH --price 75000 --json --output output_ch.json
```

---

## 🐍 Python API Beispiel

```python
from firmenwagen_dach import compare_methods, calculate_pauschale, calculate_fahrtenbuch

# Vollständiger Methodenvergleich für deutsches Elektroauto
comparison = compare_methods(
    country="DE",
    gross_list_price=68000.0,
    vehicle_type="bev",        # 0,25 % Viertelung greift bis 70k €
    distance_km=22.0,          # 0,0075 % pro km
    total_annual_costs=10500.0,
    total_annual_km=30000.0,
    private_km_annual=4500.0,  # 15 % Privatanteil
    tax_rate=0.42
)

print(f"Empfohlene Methode   : {comparison.recommended_method}")
print(f"Steuerersparnis (FB) : {comparison.tax_savings_with_fahrtenbuch:+,.2f} EUR p.a.")
print(f"Break-Even Privat-km : {comparison.break_even_private_km:,.0f} km")
```

---

## 🧪 Tests ausführen

Das Repository enthält mehr als 25 automatisierte Unit-Tests für alle Steuerklassen, CO2-Grenzwerte und Kostendeckelungen:

```bash
pip install pytest
pytest -v
```

---

## ⚖️ Rechtlicher Hinweis & Distanzierung

Reines technisches und mathematisches Berechnungs- und Simulationswerkzeug. Keine Steuer- oder Rechtsberatung im Sinne des Steuerberatungsgesetzes (StBerG) oder Rechtsdienstleistungsgesetzes (RDG). Für die individuelle steuerliche Veranlagung ist ausschließlich der Steuerpflichtige verantwortlich.

---

## 📄 Lizenz

MIT License © 2026 [DACH Digitalwerk](https://dach-digitalwerk.netlify.app/)
