"""Root conftest.py — adds project root to sys.path so doml package is importable."""
import sys
from pathlib import Path

# Ensure the project root is on sys.path so `from doml.data_scan import ...` works
# both on the host (pytest) and inside the Docker container (PROJECT_ROOT=/home/jovyan/work)
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
