"""Peer-swap experiment (Q3.3) built on the Shi et al. harness in ../harness.

Importing this package puts the harness on sys.path, so modules here can use its
`src.*` packages (prompt builders, request helpers, API clients).
"""
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent / "harness"
if str(HARNESS_DIR) not in sys.path:
    sys.path.insert(0, str(HARNESS_DIR))

# Load API keys from harness/.env explicitly, so they are found however Python is started.
try:
    from dotenv import load_dotenv
    load_dotenv(HARNESS_DIR / ".env")
except ImportError:  # only the harness venv has python-dotenv; tests don't need keys
    pass
