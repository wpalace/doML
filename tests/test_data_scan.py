"""Tests for doml.data_scan — Phase 03 INTV-03"""
import pytest
from pathlib import Path
from doml.data_scan import scan_data_folder  # noqa: F401 — will fail until module exists

FIXTURES = Path(__file__).parent / "fixtures"


def test_csv_scan():
    results = scan_data_folder(FIXTURES)
    csv_results = [r for r in results if r["format"] == "CSV"]
    assert len(csv_results) == 1
    r = csv_results[0]
    assert r["row_count"] == 3
    assert r["col_count"] == 2
    assert any(c["name"] == "id" for c in r["columns"])
    assert any(c["name"] == "value" for c in r["columns"])


def test_parquet_scan():
    results = scan_data_folder(FIXTURES)
    parquet_results = [r for r in results if r["format"] == "PARQUET"]
    assert len(parquet_results) == 1
    r = parquet_results[0]
    assert r["row_count"] == 3
    assert r["col_count"] == 2


def test_xlsx_scan():
    results = scan_data_folder(FIXTURES)
    xlsx_results = [r for r in results if r["format"] == "XLSX"]
    assert len(xlsx_results) == 1
    r = xlsx_results[0]
    assert r["row_count"] == 3
    assert r["col_count"] == 2


def test_empty_dir_raises(tmp_path):
    with pytest.raises(ValueError, match="No data files found"):
        scan_data_folder(tmp_path)


def test_missing_dir_raises(tmp_path):
    with pytest.raises(ValueError, match="not found"):
        scan_data_folder(tmp_path / "nonexistent")


def test_xls_not_supported(tmp_path):
    xls_file = tmp_path / "data.xls"
    xls_file.write_bytes(b"dummy")  # content doesn't matter — extension check is first
    with pytest.raises(ValueError, match=".xls"):
        scan_data_folder(tmp_path)
