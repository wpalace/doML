"""
doml/data_scan.py — DuckDB file introspection for data/raw/

Scans each supported file in a directory and returns shape + schema.
Called by the /doml-new-project interview before any questions are asked.

Supported: .csv (read_csv_auto), .parquet (read_parquet), .xlsx (read_xlsx via excel extension)
Not supported: .xls (legacy BIFF format — DuckDB excel extension does not support it)

REPR-02: Uses PROJECT_ROOT env var for path resolution when called from workflow.
INFR-05: Read-only scan — never writes to data/raw/.
"""
import os
import duckdb
from pathlib import Path
from typing import Union


SUPPORTED_EXTENSIONS = {'.csv', '.parquet', '.xlsx'}
UNSUPPORTED_LEGACY = {'.xls'}

ERROR_MISSING_DIR = "data/raw/ directory not found at {path}. Create the directory and copy your dataset files there."
ERROR_EMPTY_DIR = (
    "No data files found in {path}\n\n"
    "Expected at least one file in supported formats:\n"
    "  - CSV (.csv)\n"
    "  - Parquet (.parquet)\n"
    "  - Excel (.xlsx)\n\n"
    "Note: Legacy .xls format is not supported. Save as .xlsx first "
    "(File -> Save As -> Excel Workbook in Excel).\n\n"
    "Add your dataset files to data/raw/ and run /doml-new-project again."
)
ERROR_XLS_LEGACY = (
    "Legacy .xls file detected: {filename}\n\n"
    ".xls (Excel 97-2003 format) is not supported. "
    "Please save as .xlsx (File -> Save As -> Excel Workbook) and try again."
)


def scan_file(path: Path) -> dict:
    """
    Scans a single file using DuckDB and returns its schema summary.

    Returns:
        dict with keys: path (str), format (str), row_count (int), col_count (int),
                        columns (list[dict] with name + dtype)

    Raises:
        ValueError: for .xls files (detected before DuckDB call)
        Exception: propagated from DuckDB for unreadable files
    """
    suffix = path.suffix.lower()

    if suffix in UNSUPPORTED_LEGACY:
        raise ValueError(ERROR_XLS_LEGACY.format(filename=path.name))

    con = duckdb.connect()
    path_str = str(path)

    if suffix == '.csv':
        schema = con.execute(f"DESCRIBE SELECT * FROM read_csv_auto('{path_str}')").fetchall()
        row_count = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{path_str}')").fetchone()[0]
        fmt = 'CSV'
    elif suffix == '.parquet':
        schema = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{path_str}')").fetchall()
        row_count = con.execute(f"SELECT COUNT(*) FROM read_parquet('{path_str}')").fetchone()[0]
        fmt = 'PARQUET'
    elif suffix == '.xlsx':
        # excel extension autoloads on first read_xlsx call (DuckDB 1.2+, confirmed 1.5.1)
        schema = con.execute(f"DESCRIBE SELECT * FROM read_xlsx('{path_str}')").fetchall()
        row_count = con.execute(f"SELECT COUNT(*) FROM read_xlsx('{path_str}')").fetchone()[0]
        fmt = 'XLSX'
    else:
        raise ValueError(f"Unsupported file extension: {suffix}")

    con.close()

    # DESCRIBE returns: (column_name, column_type, null, key, default, extra)
    columns = [{"name": row[0], "dtype": row[1]} for row in schema]

    return {
        "path": str(path),
        "format": fmt,
        "row_count": row_count,
        "col_count": len(columns),
        "columns": columns,
    }


def scan_data_folder(data_dir: Path) -> list:
    """
    Scans all supported files in data_dir and returns a list of scan results.

    Args:
        data_dir: Path to the directory containing data files (typically data/raw/).
                  Resolved by caller using PROJECT_ROOT per REPR-02.

    Returns:
        List of scan result dicts (one per supported file). See scan_file() for dict shape.

    Raises:
        ValueError: if data_dir does not exist, is empty, or contains no supported files.
                    .xls files trigger a specific error with save-as instructions.
    """
    if not data_dir.exists():
        raise ValueError(ERROR_MISSING_DIR.format(path=data_dir))

    all_files = [f for f in data_dir.iterdir() if f.is_file()]

    # Check for legacy .xls before the supported-file count — give specific guidance
    xls_files = [f for f in all_files if f.suffix.lower() in UNSUPPORTED_LEGACY]
    if xls_files:
        raise ValueError(ERROR_XLS_LEGACY.format(filename=xls_files[0].name))

    supported_files = [f for f in all_files if f.suffix.lower() in SUPPORTED_EXTENSIONS]

    if not supported_files:
        raise ValueError(ERROR_EMPTY_DIR.format(path=data_dir))

    results = []
    for path in sorted(supported_files):
        try:
            results.append(scan_file(path))
        except Exception as exc:
            results.append({
                "path": str(path),
                "format": "ERROR",
                "error": str(exc),
                "row_count": 0,
                "col_count": 0,
                "columns": [],
            })

    return results


def format_scan_report(results: list) -> str:
    """
    Formats scan results as a human-readable string for display at the start of the interview.

    Example output:
        Data Folder Contents
        ────────────────────
        sales.csv       CSV      12,450 rows x 8 columns
          id (BIGINT), date (DATE), amount (DOUBLE), region (VARCHAR), ...
    """
    lines = ["Data Folder Contents", "-" * 40]
    for r in results:
        if r["format"] == "ERROR":
            lines.append(f"  {Path(r['path']).name:<30}  ERROR: {r['error']}")
            continue
        col_summary = ", ".join(
            f"{c['name']} ({c['dtype']})" for c in r["columns"][:6]
        )
        if len(r["columns"]) > 6:
            col_summary += f", ... (+{len(r['columns']) - 6} more)"
        lines.append(
            f"  {Path(r['path']).name:<30}  {r['format']:<8}"
            f"  {r['row_count']:>10,} rows x {r['col_count']} columns"
        )
        lines.append(f"    {col_summary}")
    return "\n".join(lines)
