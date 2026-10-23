# -*- coding: utf-8 -*-
import io
import json
from contextlib import redirect_stdout
from firmenwagen_dach.cli import run_cli, build_parser


def test_cli_parser_build():
    parser = build_parser()
    assert parser is not None
    assert parser.description is not None


def test_cli_run_de_calculation():
    f = io.StringIO()
    with redirect_stdout(f):
        code = run_cli([
            "--country", "DE",
            "--price", "50000",
            "--type", "bev",
            "--distance", "15",
            "--costs", "9000",
            "--total-km", "25000",
            "--private-km", "4000"
        ])
    assert code == 0
    output = f.getvalue()
    assert "DACH FIRMENWAGEN-VERGLEICHSRECHNER 2026 (DE)" in output
    assert "Pauschalmethode:" in output
    assert "Fahrtenbuchmethode:" in output


def test_cli_run_json_output():
    f = io.StringIO()
    with redirect_stdout(f):
        code = run_cli([
            "--country", "AT",
            "--price", "45000",
            "--co2", "110",
            "--json"
        ])
    assert code == 0
    output = f.getvalue()
    data = json.loads(output)
    assert data["country"] == "AT"
    assert data["currency"] == "EUR"
    assert "pauschale" in data
    assert "fahrtenbuch" in data


def test_cli_run_ch_calculation():
    f = io.StringIO()
    with redirect_stdout(f):
        code = run_cli([
            "--country", "CH",
            "--price", "60000",
            "--json"
        ])
    assert code == 0
    output = f.getvalue()
    data = json.loads(output)
    assert data["country"] == "CH"
    assert data["currency"] == "CHF"
    assert data["pauschale"]["total_gwv_monthly"] == 540.0  # 60k * 0.9%


def test_cli_file_export(tmp_path):
    out_file = str(tmp_path / "test_export.json")
    f = io.StringIO()
    with redirect_stdout(f):
        code = run_cli([
            "--country", "DE",
            "--price", "40000",
            "--output", out_file
        ])
    assert code == 0
    with open(out_file, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    assert data["country"] == "DE"
    assert data["pauschale"]["gross_list_price"] == 40000.0
